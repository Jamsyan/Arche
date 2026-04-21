<template>
  <div class="blog-shell">
    <header class="blog-header">
      <h1>Veil Blog</h1>
      <nav>
        <router-link to="/">Home</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.blog-shell {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}
.blog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}
</style>
