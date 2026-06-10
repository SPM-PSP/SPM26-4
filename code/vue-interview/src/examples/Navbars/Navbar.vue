<template> 
  <nav
    class="shadow-none navbar navbar-main navbar-expand-lg border-radius-xl"
    v-bind="$attrs"
    id="navbarBlur"
    data-scroll="true"
  >
    <div class="px-3 py-1 container-fluid">
      <!-- 可选：breadcrumbs 可保留或删 -->
      <!-- <breadcrumbs :currentPage="currentRouteName" :textWhite="textWhite" /> -->

      <div
        class="mt-2 collapse navbar-collapse mt-sm-0 me-md-0 me-sm-4"
        :class="$store.state.isRTL ? 'px-0' : 'me-sm-4'"
        id="navbar"
      >
        <!-- 输入框占位 -->
        <div
          class="pe-md-3 d-flex align-items-center"
          :class="$store.state.isRTL ? 'me-md-auto' : 'ms-md-auto'"
          style="height: 40px;"
        >
          <div style="width: 250px;"></div>
        </div>

        <!-- 图标占位区域 -->
        <ul class="navbar-nav justify-content-end">
          <!-- 用户图标占位 -->
          <li class="nav-item d-flex align-items-center">
            <span class="px-0 nav-link font-weight-bold text-body">
              <span style="width: 16px; height: 16px; display: inline-block;"></span>
            </span>
          </li>

          <!-- 侧边栏三条线占位 -->
          <li class="nav-item d-xl-none ps-3 d-flex align-items-center">
            <span class="p-0 nav-link text-body" id="iconNavbarSidenav">
              <div class="sidenav-toggler-inner">
                <span class="sidenav-toggler-line" style="opacity: 0;"></span>
                <span class="sidenav-toggler-line" style="opacity: 0;"></span>
                <span class="sidenav-toggler-line" style="opacity: 0;"></span>
              </div>
            </span>
          </li>

          <!-- 设置图标占位 -->
          <li class="px-3 nav-item d-flex align-items-center">
            <span class="p-0 nav-link text-body">
              <span style="width: 16px; height: 16px; display: inline-block;"></span>
            </span>
          </li>

          <!-- 通知图标占位 -->
          <li class="nav-item d-flex align-items-center pe-2">
            <span class="p-0 nav-link text-body">
              <span style="width: 16px; height: 16px; display: inline-block;"></span>
            </span>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "navbar",
  props: ["minNav", "textWhite"],
  computed: {
    currentRouteName() {
      return this.$route.name;
    },
  },
  updated() {
    const navbar = document.getElementById("navbarBlur");
    window.addEventListener("scroll", () => {
      if (window.scrollY > 10 && this.$store.state.isNavFixed) {
        navbar.classList.add("blur", "position-sticky", "shadow-blur");
      } else {
        navbar.classList.remove("blur", "position-sticky", "shadow-blur");
      }
    });
  },
};
</script>

