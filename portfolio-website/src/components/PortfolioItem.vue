<template>
  <v-container class="fill-height">
    <v-carousel>
      <v-carousel-item
        v-for="c in category.images"
        :key="c"
        :src="c.src"
        cover
      ></v-carousel-item>
    </v-carousel>
  </v-container>
</template>

<script lang="ts">
import roboticsTile from "@/assets/images/robotics.jpeg";
import legoTile from "@/assets/images/legos.jpeg";
import origamiTile from "@/assets/images/origami.jpeg";
import certsTile from "@/assets/images/certificates.jpeg";

const categories: any = {
  lego: {
    name: "lego",
    images: [
      {
        src: roboticsTile
      },
      {
        src: legoTile
      },
      {
        src:origamiTile
      },
      {
        src: certsTile
      },
    ],
  },
  robotics: {
    name: "robotics",
    images: [
      {
        src: "https://cdn.vuetifyjs.com/images/carousel/squirrel.jpg",
      },
    ],
  },
  origamies: {
    name: "origamies",
    images: [
      {
        src: "https://cdn.vuetifyjs.com/images/carousel/squirrel.jpg",
      },
    ],
  },
  certs: {
    name: "certs",
    images: [
      {
        src: "https://cdn.vuetifyjs.com/images/carousel/squirrel.jpg",
      },
    ],
  },
};

export default {
  name: "PortfolioItem",
  data: () => {
    category: {}
  },
  computed: {
    category() {
      const name: any = this.$route.params.name;
      return categories[name];
    },
  },
};
</script>
