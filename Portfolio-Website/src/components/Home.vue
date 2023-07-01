<template>
  <v-app id="inspire">
    <v-app-bar app extended>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>

      <v-toolbar-title>Application</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col cols="0">
            <v-card title="This is a title" subtitle="This is a subtitle" text="This is content"></v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-card height="200" title="This is a title" subtitle="This is a subtitle" text="This is content"></v-card>
          </v-col>
          <v-col>
            <v-card height="200" title="This is a title" subtitle="This is a subtitle" text="This is content"></v-card>
          </v-col>
          <v-col>
            <v-card height="200" title="This is a title" subtitle="This is a subtitle" text="This is content"></v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts">
export default {
  name: 'Home',
}
</script>
