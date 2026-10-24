<template>
  <v-container class="fill-height">
      <vue-pdf-embed :source="resumePdf" />
  </v-container>
</template>

<script lang="ts">
import VuePdfEmbed from 'vue-pdf-embed'
import AliFakiraPdf from '@/assets/docs/Ali-Fakira.pdf'

export default {
  components: {
    VuePdfEmbed,
  },
  name: "Resume",
  data: () => ({
    resumePdf: AliFakiraPdf
  }),
};
</script>
