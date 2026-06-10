<template>
  <div>
    <navbar btn-background="bg-gradient-primary" />
    <div
      class="pt-5 m-3 page-header align-items-start min-vh-50 pb-11 border-radius-lg"
      :style="{
        backgroundImage:
          'url(' + require('@/assets/img/curved-images/curved6.jpg') + ')',
      }"
    >
      <span class="mask bg-gradient-dark opacity-6"></span>
      <div class="container">
        <div class="row justify-content-center">
          <div class="mx-auto text-center col-lg-5">
            <h1 class="mt-5 mb-2 text-white">欢迎!</h1>
            <p class="text-white text-lead">
              注册您的新账户
            </p>
          </div>
        </div>
      </div>
    </div>
    <div class="container">
      <div class="row mt-lg-n10 mt-md-n11 mt-n10 justify-content-center">
        <div class="mx-auto col-xl-4 col-lg-5 col-md-7">
          <div class="card z-index-0">
            <div class="pt-4 text-center card-header">
              <h5>用户注册</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="handleSubmit">
                <div class="mb-3">
                  <label for="accountID" class="form-label">账号*</label>
                  <soft-input
                    id="accountID"
                    v-model="form.accountID"
                    type="text"
                    placeholder="请输入账号"
                    aria-label="Account ID"
                    :class="{ 'is-invalid': errors.accountID }"
                  />
                  <div v-if="errors.accountID" class="invalid-feedback">{{ errors.accountID }}</div>
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">密码*</label>
                  <soft-input
                    id="password"
                    v-model="form.password"
                    type="password"
                    placeholder="请输入密码"
                    aria-label="Password"
                    :class="{ 'is-invalid': errors.password }"
                  />
                  <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
                </div>
                <div class="mb-3">
                  <label for="nickName" class="form-label">昵称*</label>
                  <soft-input
                    id="nickName"
                    v-model="form.nickName"
                    type="text"
                    placeholder="请输入昵称"
                    aria-label="Nickname"
                    :class="{ 'is-invalid': errors.nickName }"
                  />
                  <div v-if="errors.nickName" class="invalid-feedback">{{ errors.nickName }}</div>
                </div>
                <div class="mb-3">
                  <label for="schoolName" class="form-label">学校名称*</label>
                  <soft-input
                    id="schoolName"
                    v-model="form.schoolName"
                    type="text"
                    placeholder="请输入学校名称"
                    aria-label="School Name"
                    :class="{ 'is-invalid': errors.schoolName }"
                  />
                  <div v-if="errors.schoolName" class="invalid-feedback">{{ errors.schoolName }}</div>
                </div>
                <div class="mb-3">
                  <label for="major" class="form-label">专业*</label>
                  <soft-input
                    id="major"
                    v-model="form.major"
                    type="text"
                    placeholder="请输入专业"
                    aria-label="Major"
                    :class="{ 'is-invalid': errors.major }"
                  />
                  <div v-if="errors.major" class="invalid-feedback">{{ errors.major }}</div>
                </div>
                <div class="mb-3">
                  <label for="qualification" class="form-label">学历*</label>
                  <select
                    id="qualification"
                    v-model="form.qualification"
                    class="form-control"
                    :class="{ 'is-invalid': errors.qualification }"
                  >
                    <option disabled value="">请选择学历</option>
                    <option>高职</option>
                    <option>本科</option>
                    <option>研究生</option>
                    <option>博士</option>
                  </select>
                  <div v-if="errors.qualification" class="invalid-feedback">{{ errors.qualification }}</div>
                </div>
                 <div class="mb-3">
                  <label for="grade" class="form-label">年级*</label>
                  <soft-input
                    id="grade"
                    v-model="form.grade"
                    type="text"
                    placeholder="例如：大三、研二"
                    aria-label="Grade"
                    :class="{ 'is-invalid': errors.grade }"
                  />
                  <div v-if="errors.grade" class="invalid-feedback">{{ errors.grade }}</div>
                </div>
                <div class="mb-3">
                  <label for="birthday" class="form-label">生日(可选)</label>
                  <soft-input
                    id="birthday"
                    v-model="form.birthday"
                    type="date"
                    aria-label="Birthday"
                  />
                </div>
                <div class="mb-3">
                  <label for="avatar" class="form-label">头像(可选)</label>
                  <input
                    id="avatar"
                    type="file"
                    @change="onAvatarChange"
                    accept="image/*"
                    class="form-control"
                  />
                </div>
                <div class="mb-3">
                  <label for="resume" class="form-label">简历PDF(可选)</label>
                  <input
                    id="resume"
                    type="file"
                    @change="onResumeChange"
                    accept="application/pdf"
                    class="form-control"
                  />
                </div>
                <div class="text-center">
                  <soft-button
                    type="submit"
                    color="dark"
                    full-width
                    variant="gradient"
                    class="my-4 mb-2"
                  >
                    注册
                  </soft-button>
                </div>
                <p class="text-sm mt-3 mb-0">
                  已有账户？
                  <router-link :to="{ name: 'Sign In' }" class="text-dark font-weight-bolder">
                    登录
                  </router-link>
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 注册成功弹窗 -->
    <div v-if="showSuccessModal" class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">注册成功</h5>
            <button type="button" class="btn-close" @click="closeModalAndRedirect"></button>
          </div>
          <div class="modal-body">
            <p>您的账号已成功注册！即将跳转到登录页面...</p>
          </div>
          <div class="modal-footer">
            <soft-button color="dark" @click="closeModalAndRedirect">确定</soft-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from "@/examples/PageLayout/Navbar.vue";
import SoftInput from "@/components/SoftInput.vue";
import SoftButton from "@/components/SoftButton.vue";
import { mapMutations } from "vuex";
import axios from 'axios';

export default {
  name: "SignUp",
  components: {
    Navbar,
    SoftInput,
    SoftButton,
  },
  data() {
    return {
      form: {
        accountID: "",
        password: "",
        nickName: "",
        schoolName: "",
        major: "",
        qualification: "",
        grade: "", 
        birthday: "",
        avatar: null,
        resume: null,
      },
      errors: {
        accountID: "",
        password: "",
        nickName: "",
        schoolName: "",
        major: "",
        qualification: "",
        grade: "", 
      },
      showSuccessModal: false,
    };
  },
  methods: {
    ...mapMutations(["toggleEveryDisplay", "toggleHideConfig"]),
    
    validateForm() {
      let isValid = true;
      // 重置错误信息
      this.errors = { accountID: "", password: "", nickName: "", schoolName: "", major: "", qualification: "", grade: "" };
      
      if (!this.form.accountID.trim()) {
        this.errors.accountID = "请输入账号";
        isValid = false;
      }
      if (!this.form.password) {
        this.errors.password = "请输入密码";
        isValid = false;
      }
      if (!this.form.nickName.trim()) {
        this.errors.nickName = "请输入昵称";
        isValid = false;
      }
      if (!this.form.schoolName.trim()) {
        this.errors.schoolName = "请输入学校名称";
        isValid = false;
      }
      if (!this.form.major.trim()) {
        this.errors.major = "请输入专业";
        isValid = false;
      }
      if (!this.form.qualification) {
        this.errors.qualification = "请选择学历";
        isValid = false;
      }
      if (!this.form.grade.trim()) {
        this.errors.grade = "请输入年级";
        isValid = false;
      }
      
      return isValid;
    },
    
    async handleSubmit() {
      if (!this.validateForm()) return;

      const formData = new FormData();

      const userData = {
        accountID: this.form.accountID,
        password: this.form.password,
        nickName: this.form.nickName,
        schoolName: this.form.schoolName,
        major: this.form.major,
        qualification: this.form.qualification,
        grade: this.form.grade, 
      };
      
      if (this.form.birthday) {
        userData.birthday = `${this.form.birthday}T00:00:00`;
      }
      formData.append('user_data_json', JSON.stringify(userData));

      if (this.form.avatar) {
        formData.append('avatar_file', this.form.avatar);
      }

      if (this.form.resume) {
        formData.append('resume_file', this.form.resume);
      }

      try {
        const res = await axios.post("http://localhost:8000/api/users/register", formData, {
        });
        if (res.data.code === 201) {
          this.showSuccessModal = true;
          setTimeout(this.closeModalAndRedirect, 2000); 
        }
      } catch (err) {
        const errorMessage = err.response?.data?.detail?.[0]?.msg || err.response?.data?.message || "注册失败，账号可能已被使用或信息有误。";
        alert(`注册失败: ${errorMessage}`);
        console.error("Registration error:", err.response?.data);
      }
    },
    
    closeModalAndRedirect() {
      this.showSuccessModal = false;
      this.$router.push({ name: 'Sign In' }); 
    },
    
    onAvatarChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.form.avatar = file;
      }
    },
    
    onResumeChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.form.resume = file;
      }
    }
  },
  created() {
    this.toggleEveryDisplay();
    this.toggleHideConfig();
  },
  beforeUnmount() {
    this.toggleEveryDisplay();
    this.toggleHideConfig();
  },
};
</script>

<style scoped>
.invalid-feedback {
  display: block;
  color: #dc3545;
  font-size: 0.875em;
  margin-top: 0.25rem;
}
.is-invalid {
  border-color: #dc3545;
}
.page-header {
  background-size: cover;
  background-position: center;
}
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1050;
  overflow: hidden;
  outline: 0;
}
.modal.show {
  display: block;
}
</style>