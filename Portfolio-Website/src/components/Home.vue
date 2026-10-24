<!-- @vue-skip -->
<template>
  <v-container class="fill-height fluid" style="min-height: 434px">
    <v-fade-transition mode="out-in">
      <v-container>
        <!-- LEFT" -->
        <v-row v-for="c in catetories" :key="c.id" class="mb-4">
          <v-card border="none" variant="plain">
            <v-card-title> <p class="text-capitalize h-3">{{ c.title }}</p></v-card-title>
            <v-card-subtitle>
              <span>{{c.subtitle}}</span>

              <v-icon
                color="error"
                :icon="c.icon"
                size="small"
              ></v-icon>
            </v-card-subtitle>
            <v-col>
              <v-card-text class="p-0">
              {{ c.text }}
              </v-card-text>
            </v-col>
            <v-col>
              <v-carousel class="p-2 m-2">
                <v-carousel-item
                  v-for="i in c.images"
                  :key="i"
                  :src="i.src"
                  cover
                ></v-carousel-item>
              </v-carousel>
            </v-col>
          </v-card>
        </v-row>
      </v-container>
    </v-fade-transition>
  </v-container>
  <!--Main Content end -->
</template>

<script lang="ts">
import roboticsTile from "@/assets/images/robotics.jpeg";
import legoTile from "@/assets/images/legos.jpeg";
import origamiTile from "@/assets/images/origami.jpeg";
import certsTile from "@/assets/images/certificates.jpeg";

export default {
  name: "Home",
  data: () => ({
    catetories: [
      {
        id: 1,
        title: "Lego",
        subtitle: "I love legos",
        text: "I have always had a pation for legos. This is something and another that comes from the essay and speaks to what's made me who I am today.",
        class: "text-left",
        icon: "mdi-fire-circle",
        img: legoTile,
        images: [
          {
            src: roboticsTile,
          },
          {
            src: legoTile,
          },
          {
            src: origamiTile,
          },
          {
            src: certsTile,
          },
        ],
      },
      {
        id: 2,
        title: "Robotics",
        subtitle: "I love robotics",
        text: "I have always had a pation for legos. This is something and another that comes from the essay and speaks to what's made me who I am today.",
        img: roboticsTile,
        class: "text-right",
        icon: "mdi-fire-circle",
        images: [
          {
            src: roboticsTile,
          },
          {
            src: legoTile,
          },
          {
            src: origamiTile,
          },
          {
            src: certsTile,
          },
        ],
      },
      {
        id: 3,
        title: "Origamies",
        subtitle: "I love Origamies",
        text: "I have always had a pation for legos. This is something and another that comes from the essay and speaks to what's made me who I am today.",
        img: origamiTile,
        class: "text-left",
        icon: "mdi-fire-circle",
        images: [
          {
            src: roboticsTile,
          },
          {
            src: legoTile,
          },
          {
            src: origamiTile,
          },
          {
            src: certsTile,
          },
        ],
      },
      {
        id: 4,
        title: "Certificates",
        subtitle: "Certificates",
        text: "I have always had a pation for legos. This is something and another that comes from the essay and speaks to what's made me who I am today.",
        img: certsTile,
        class: "text-right",
        icon: "mdi-fire-circle",
        images: [
          {
            src: roboticsTile,
          },
          {
            src: legoTile,
          },
          {
            src: origamiTile,
          },
          {
            src: certsTile,
          },
        ],
      },
    ],
  }),
  methods: {
    readItem(name: string) {
      const params = { name: name };
      this.$router.push({ name: "item", params });
    },
  },
};
</script>
