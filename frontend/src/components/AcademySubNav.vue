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

<style scoped>
.academy-subnav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.academy-subnav a {
  text-decoration: none;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--muted);
}

.academy-subnav a.active {
  background: rgba(31, 107, 74, 0.12);
  color: var(--ink);
  border-color: transparent;
}
</style>
