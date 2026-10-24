<template>
  <v-app>
    <v-main class="flex align-center">
      <v-app-bar
        height="100" class="ps-6"
        image="@/assets/images/block-bg.jpeg"
        gradient="to top right, rgba(19,84,122,.8), rgba(128,208,199,.8)">
        
        <template v-slot:prepend >
          <v-btn size="x-large" icon to="/">
            <v-icon>mdi-robot-angry</v-icon>
          </v-btn>
        </template>

        <v-app-bar-title to="/" class="text-h3 font-weight-bold align-center" width="100%" height="100">
          <!-- <v-btn plain to="/"> -->
            Ali Fakira's Portfolio
          <!-- </v-btn> -->
        </v-app-bar-title>

        <template v-slot:append>
          <v-btn size="x-large" icon to="/resume">
            <v-icon>mdi-account-tie</v-icon>
          </v-btn>
        </template>
      </v-app-bar>
      
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Home from "./components/Home.vue";
import Resume from "./components/Resume.vue";

export default {
  name: "App",

  components: {
    Home,
    Resume,
  },

  data: () => ({}),
};
</script>
