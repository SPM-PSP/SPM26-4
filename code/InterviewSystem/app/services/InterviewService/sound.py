import hashlib
import hmac
import base64
import json
import threading
import ssl
import websocket
import traceback
import math
import pydub
import os
from urllib.parse import urlencode
from email.utils import formatdate
from langgraph.graph import StateGraph
from typing import TypedDict, Dict, Any, List

#API限制常量 (字节)，由于我们的完整面试视频是超过了官方要求的大小的限制，所以我们在进行语音转文本、语音分析的时候采用分段发送的办法。
MAX_AUDIO_B64_BYTES = 10485760 - 1024
MAX_TEXT_BYTES = 4096 - 100


#定义状态结构
class EvaluationState(TypedDict):
    audio_path: str
    ref_text: str
    evaluation_results: List[Dict[str, Any]]
    rhythm_score: int
    rhythm_desc: str
    speed_score: float
    speed_desc: str
    error: bool
    error_message: str


#SuntoneEvaluator
class SuntoneEvaluator:
    def __init__(self, app_id, api_key, api_secret,
                 host="cn-east-1.ws-api.xf-yun.com",
                 path="/v1/private/s8e098720"):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = host
        self.path = path
        self.url = f"wss://{host}{path}"
        self.ws = None
        self.complete = threading.Event()
        self.response_json = None
        self.audio_path = None
        self.ref_text = None

    def getURL(self):
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode()
        auth_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        authorization = base64.b64encode(auth_origin.encode()).decode()
        query = urlencode({"host": self.host, "date": date, "authorization": authorization})
        return f"{self.url}?{query}"

    def requestPayload(self, audio_b64: str, ref_text: str) -> dict:
        return {
            "header": {"app_id": self.app_id, "status": 2},
            "parameter": {"st": {"lang": "cn", "core": "para", "refText": ref_text,
                                 "result": {"encoding": "utf8", "compress": "raw", "format": "plain"}}},
            "payload": {"data": {"encoding": "lame", "sample_rate": 16000, "channels": 1, "bit_depth": 16, "status": 2,
                                 "seq": 0, "audio": audio_b64, "frame_size": 0}}
        }

    def on_open(self, ws):
        def run():
            try:
                with open(self.audio_path, "rb") as f:
                    raw_audio = f.read()
                audio_b64 = base64.b64encode(raw_audio).decode()
                audio_b64_len = len(audio_b64.encode('utf-8'))
                ref_text_len = len(self.ref_text.encode('utf-8'))
                #print(
                #    f"DEBUG: Preparing to send chunk. Audio_b64 size: {audio_b64_len} bytes, Text size: {ref_text_len} bytes.")
                if audio_b64_len > MAX_AUDIO_B64_BYTES or ref_text_len > MAX_TEXT_BYTES:
                    error_msg = f"Audio size ({audio_b64_len}) or text size ({ref_text_len}) exceeds limit."
                    self.response_json = {"error": True, "message": f"Pre-flight check failed: {error_msg}"}
                    self.complete.set()
                    if ws and ws.keep_running: ws.close()
                    return
                payload = self.requestPayload(audio_b64, self.ref_text)
                ws.send(json.dumps(payload))
            except Exception as e:
                self.response_json = {"error": True, "message": f"Failed to send data: {e}"}
                self.complete.set()
                if ws and ws.keep_running: ws.close()

        threading.Thread(target=run).start()


    def on_message(self, ws, message):
        should_close = False
        try:
            data = json.loads(message)
            header = data.get("header", {})

            #判断服务器请求失败
            if header.get("code", -1) != 0:
                self.response_json = {"error": True, "message": header.get("message", "Unknown API header error")}
                should_close = True
                return

            #判断服务请求成功
            result = data.get("payload", {}).get("result", {})
            # 判断成功的依据是'text'字段的存在
            if isinstance(result, dict) and "text" in result:
                text_b64 = result.get("text", "")
                self.response_json = json.loads(base64.b64decode(text_b64).decode())
                should_close = True
                return

            # 其他的一些错误
            print(f"DEBUG: Received a non-final message, waiting... Content: {data}")

        except Exception as e:
            self.response_json = {"error": True, "message": f"Failed to parse message: {e}"}
            should_close = True
        finally:
            if should_close:
                self.complete.set()
                if ws and ws.keep_running:
                    ws.close()

    def on_error(self, ws, error):
        if not self.response_json: self.response_json = {"error": True, "message": str(error)}
        self.complete.set()

    def on_close(self, ws, close_status_code, close_msg):
        if not self.complete.is_set():
            if not self.response_json: self.response_json = {"error": True,
                                                             "message": "Connection closed unexpectedly."}
            self.complete.set()

    def evaluate(self, audio_path: str, ref_text: str, timeout: float = 60):
        self.audio_path = audio_path
        self.ref_text = ref_text
        self.complete.clear()
        self.response_json = None
        try:
            auth_url = self.getURL()
            self.ws = websocket.WebSocketApp(auth_url, on_open=self.on_open, on_message=self.on_message,
                                             on_error=self.on_error, on_close=self.on_close)
            thread = threading.Thread(target=self.ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
            thread.daemon = True
            thread.start()
            self.complete.wait(timeout=timeout)
            if not self.complete.is_set(): return {"error": True, "message": "Evaluation timed out"}
            return self.response_json
        except Exception as e:
            return {"error": True, "message": f"WebSocket setup failed: {e}"}



def split_audio_and_text(audio_path, text):
    try:
        print("DEBUG: Loading audio file...")
        audio = pydub.AudioSegment.from_file(audio_path)
        print(f"DEBUG: Audio loaded. Duration: {len(audio) / 1000:.2f}s")
        chunk_duration_ms = 60 * 1000
        duration_ms = len(audio)
        if duration_ms == 0: return []
        chars_per_ms = len(text) / duration_ms
        chunks = []
        for i, start_ms in enumerate(range(0, duration_ms, chunk_duration_ms)):
            end_ms = start_ms + chunk_duration_ms
            audio_chunk = audio[start_ms:end_ms]
            text_start_index = math.floor(start_ms * chars_per_ms)
            text_end_index = math.ceil(end_ms * chars_per_ms)
            text_chunk = text[text_start_index:text_end_index]
            if len(audio_chunk) > 500 and text_chunk.strip():
                chunk_path = f"{audio_path}_chunk_{i}.mp3"
                print(f"DEBUG: Exporting chunk {i} to {chunk_path}...")
                audio_chunk.export(chunk_path, format="mp3", bitrate="128k")
                print(f"DEBUG: Chunk {i} exported. File size: {os.path.getsize(chunk_path)} bytes.")
                chunks.append({"audio_path": chunk_path, "ref_text": text_chunk, "duration": len(audio_chunk)})
        return chunks
    except Exception as e:
        print(f"错误: 音频/文本分块失败 - {e}")
        traceback.print_exc()
        return []


def evaluate_node(state: EvaluationState) -> EvaluationState:
    chunks = split_audio_and_text(state["audio_path"], state["ref_text"])
    if not chunks:
        state["evaluation_results"] = [{"result": {"error": True, "message": "音频分块失败或无有效内容"}}]
        return state
    evaluator = SuntoneEvaluator(app_id="f53357ff", api_key="4c3b3f50f26078081ac259ed196346d3",
                                 api_secret="NTU3ODljZTg1ODdlNjg2ODgyOWNjM2Iz")
    results = []
    for i, chunk in enumerate(chunks):
        print(f"正在评测分块 {i + 1}/{len(chunks)}...")
        result = evaluator.evaluate(chunk["audio_path"], chunk["ref_text"])
        results.append({"result": result, "duration": chunk.get("duration", 0)})
        try:
            if os.path.exists(chunk["audio_path"]): os.remove(chunk["audio_path"])
        except Exception:
            pass
    state["evaluation_results"] = results
    return state


def score_node(state: EvaluationState) -> EvaluationState:
    results_with_duration = state.get("evaluation_results", [])
    valid_results = [r for r in results_with_duration if
                     isinstance(r.get("result"), dict) and not r["result"].get("error")]
    if not valid_results:
        state["error"] = True
        first_error_item = results_with_duration[0] if results_with_duration else {}
        first_error_result = first_error_item.get("result") if isinstance(first_error_item, dict) else {}
        if not isinstance(first_error_result, dict): first_error_result = {"message": "未知的评测结果格式"}
        state["error_message"] = f"API调用失败: {first_error_result.get('message', '无有效评测结果')}"
    else:
        total_duration = sum(r["duration"] for r in valid_results)
        if total_duration == 0:
            state["error"] = True
            state["error_message"] = "所有有效分块时长为0"
        else:
            avg_rhythm = sum(r["result"]["result"]["rhythm"] * r["duration"] for r in valid_results) / total_duration
            avg_speed = sum(r["result"]["result"]["speed"] * r["duration"] for r in valid_results) / total_duration
            rhythm_score, rhythm_desc = score_rhythm(avg_rhythm)
            speed_score, speed_desc = score_speed(avg_speed)
            state["rhythm_score"] = int(rhythm_score)
            state["rhythm_desc"] = rhythm_desc
            state["speed_score"] = speed_score
            state["speed_desc"] = speed_desc
            state["error"] = False
            state["error_message"] = ""
            return state
    state["rhythm_score"] = 0
    state["rhythm_desc"] = state.get("error_message", "分析失败")
    state["speed_score"] = 0.0
    state["speed_desc"] = state.get("error_message", "分析失败")
    return state


def score_rhythm(rhythm):
    rhythm = int(rhythm)
    if rhythm >= 85:
        return rhythm, "语调自然流畅"
    elif rhythm >= 60:
        return rhythm, "语调稍显平淡"
    else:
        return rhythm, "语调较为生硬"


def score_speed(speed_wpm):
    speed_wpm = int(speed_wpm)
    if 120 <= speed_wpm <= 180:
        return 100, f"语速适中 {speed_wpm}字/分钟"
    elif speed_wpm < 120:
        return max(0, 100 - (120 - speed_wpm) * 0.5), f"语速偏慢 {speed_wpm}字/分钟"
    else:
        return max(0, 100 - (180 - speed_wpm) * 0.5), f"语速偏快 {speed_wpm}字/分钟"


def build_langgraph():
    workflow = StateGraph(EvaluationState)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("score", score_node)
    workflow.set_entry_point("evaluate")
    workflow.add_edge("evaluate", "score")
    workflow.set_finish_point("score")
    return workflow.compile()


def evaluate_from_input(audio_path: str, ref_text: str) -> dict:
    default_error_return = {"rhythm_score": 0, "speed_score": 0.0, "error": True, "rhythm_desc": "分析失败",
                            "speed_desc": "分析失败", "message": "未知错误"}
    if not ref_text or not ref_text.strip():
        default_error_return["message"] = "输入文本为空";
        default_error_return["rhythm_desc"] = "无有效语音内容";
        default_error_return["speed_desc"] = "无有效语音内容"
        return default_error_return
    try:
        graph = build_langgraph()
        result = graph.invoke({"audio_path": audio_path, "ref_text": ref_text})
        return {"rhythm_score": result.get("rhythm_score", 0), "rhythm_desc": result.get("rhythm_desc", "分析失败"),
                "speed_score": result.get("speed_score", 0.0), "speed_desc": result.get("speed_desc", "分析失败"),
                "error": result.get("error", False), "message": result.get("error_message", "")}
    except Exception as e:
        traceback.print_exc()
        default_error_return["message"] = f"工作流错误: {e}";
        default_error_return["rhythm_desc"] = "工作流错误";
        default_error_return["speed_desc"] = "工作流错误"
        return default_error_return


