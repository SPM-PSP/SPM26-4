<template>
  <main class="mt-0 main-content main-content-bg">
    <section>
      <div class="page-header min-vh-75">
        <div class="container">
          <div class="row">
            <div class="mx-auto col-xl-4 col-lg-5 col-md-6 d-flex flex-column">
              <div class="mt-8 card card-plain">
                <div class="pb-0 card-header text-start">
                  <h3 class="font-weight-bolder text-success text-gradient">
                    欢迎回来
                  </h3>
                  <p class="mb-0">输入账号和密码登录</p>
                </div>
                <div class="card-body">
                  <form @submit.prevent="handleSubmit" role="form" class="text-start">
                    <label for="accountID">账号</label>
                    <soft-input
                      id="accountID"
                      v-model="form.accountID"
                      type="text"
                      placeholder="Account ID"
                      name="accountID"
                    />

                    <label for="password">密码</label>
                    <soft-input
                      id="password"
                      v-model="form.password"
                      type="password"
                      placeholder="Password"
                      name="password"
                    />

                    <div class="text-center">
                      <soft-button
                        type="submit"
                        class="my-4 mb-2"
                        variant="gradient"
                        color="success"
                        full-width
                      >
                        登录
                      </soft-button>
                    </div>
                  </form>
                </div>
                <div class="px-1 pt-0 text-center card-footer px-lg-2">
                  <p class="mx-auto mb-4 text-sm">
                    没有账号?
                    <router-link
                      :to="{ name: 'Sign Up' }"
                      class="text-success text-gradient font-weight-bold"
                    >
                      注册
                    </router-link>
                  </p>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="top-0 oblique position-absolute h-100 d-md-block d-none me-n8">
                <div
                  class="bg-cover oblique-image position-absolute fixed-top ms-auto h-100 z-index-0 ms-n6"
                  :style="{
                    backgroundImage: 'url(' + require('@/assets/img/curved-images/curved9.jpg') + ')',
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import SoftInput from "@/components/SoftInput.vue";
import SoftButton from "@/components/SoftButton.vue";
import { mapMutations } from "vuex";
import axios from "axios";

export default {
  name: "SignIn",
  components: {
    SoftInput,
    SoftButton,
  },
  data() {
    return {
      form: {
        accountID: "",
        password: "",
      },
    };
  },
  methods: {
    ...mapMutations(["toggleEveryDisplay", "toggleHideConfig"]),
    async handleSubmit() {
      if (!this.form.accountID.trim() || !this.form.password) {
        alert("账号和密码不能为空");
        return;
      }
      try {
        const loginRes = await axios.post("http://localhost:8000/api/users/login", {
          accountID: this.form.accountID,
          password: this.form.password,
        });

        if (loginRes.data.code === 200) {
          // 使用localStorage保存登录的账号
          localStorage.setItem("account", this.form.accountID);
          // 传递 accountID 到个人中心页面
          this.$router.push({
            name: "Profile",
            query: {
              accountID: this.form.accountID
            }
          });
        } else {
          alert("登录失败：" + loginRes.data.message);
        }
      } catch (error) {
        alert(error.response?.data?.message || "登录失败，请稍后重试");
      }
    },
  },
  created() {
    this.toggleEveryDisplay();
    this.toggleHideConfig();
    document.body.classList.remove("bg-gray-100");
  },
  beforeUnmount() {
    this.toggleEveryDisplay();
    this.toggleHideConfig();
    document.body.classList.add("bg-gray-100");
  },
};
</script>
