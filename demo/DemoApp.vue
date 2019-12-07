<template>
  <div id="app">
    <HelloWorld msg="Welcome to Your Vue.js App"/>
    <BookForm :pk="1" @success="on_success"></BookForm>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
import BookForm from "./components/BookForm";

export default {
  name: 'app',
  components: {
    BookForm,
    HelloWorld
  },
  methods:{
    on_success: (obj) => {
      alert(JSON.stringify(obj));
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
