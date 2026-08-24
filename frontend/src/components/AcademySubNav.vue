<template>
  <nav class="academy-subnav" aria-label="Academy sections" data-testid="academy-subnav">
    <RouterLink to="/academy" exact-active-class="active">Courses</RouterLink>
    <RouterLink to="/academy/community-safety" active-class="active">Community Safety</RouterLink>
    <RouterLink to="/academy/progress" active-class="active">My Progress</RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>
