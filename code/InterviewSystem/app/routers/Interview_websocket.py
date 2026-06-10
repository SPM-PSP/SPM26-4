from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import os
import asyncio



router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(   #统一的参数请求格式
        websocket: WebSocket,
        id: str = Query(..., description="用户账号ID"),
        date: str = Query(..., description="日期：格式如2025-07-09 00:00:00"),
        resume: str = Query(..., description="简历文件路径"),
        selected_job: str = Query(..., description="面试岗位"),
):
    await websocket.accept()
    #print(f"websocket 连接已建立：{websocket.client}, user_id:{id}")

    current_file = os.path.dirname(os.path.abspath(__file__))       #获取当前脚本文件绝对路径
    package_root = os.path.abspath(os.path.join(current_file, os.pardir, os.pardir))

    #定义面试对话管理类，管理类定义在InterviewService.py服务脚本中，一次面试流程只创建一个类，保存每一个有效面试片段
    #提取音频片段并调用大模型或查看数据库提出面试问题
    #面试完成后，也是使用session_manager中方法合并全部的有效片段，闭关调用最后的分析生成有效的综合评测报告
    from app.services.InterviewService.InterviewService import InterviewServiceManager

    session_manager = InterviewServiceManager(
        user_id=id, date=date, package_root=package_root,
        resume_path=resume, job=selected_job,
    )

    try:
        # 首次连接，发送第一个通用性的问题，(是否是首次连接并发送通用问题在Service服务函数中确定)“请简单做一下自我介绍”
        first_question = await session_manager.processLastVideo_getQuestion()
        await websocket.send_text(first_question)       #等待发送当前问题，再继续保存新的片段
        session_manager.startNewFragment()

        while True: #循环调用，依次处理每一个有效片段，直到面试结束
            try:
                data = await asyncio.wait_for(     #异步等待前端传输数据，整个面试过程中的有效片段由前端判断，前端每次只传输有效的视频片段
                    websocket.receive_bytes(),
                    timeout=session_manager.SILENCE_TIMEOUT #数据接收的超时时间这里设置为的是12s
                )
                session_manager.writeVideoChunk(data)

            except asyncio.TimeoutError:    #数据流传输超时>12s
                print(f"数据流超时，一个回答结束，开始处理...")
                session_manager.stopCurrentFragment() #立即停止当前片段的写入操作

                # 获取下一个问题，这个过程是异步非阻塞的
                question = await session_manager.processLastVideo_getQuestion()

                # 检查是否是面试结束的信号
                if "面试结束" in (question or ""):
                    await websocket.send_text(question)
                    break  # 跳出循环，进入finally块

                await websocket.send_text(question)
                session_manager.startNewFragment()

    except WebSocketDisconnect:
        #print(f"Websocket 连接已断开：{websocket.client}, id:{id}")
        session_manager.stopCurrentFragment()
    except Exception as e:
        #print(f"WebSocket处理中发生错误：{e}, user_id:{id}")
        session_manager.stopCurrentFragment()
    finally:
        # 将最终的合并和分析任务提交到后台，然后立即关闭连接
        session_manager.backgroundFinalize()
        #print(f"用户 {id} 的会话已提交最终处理，WebSocket连接关闭。")