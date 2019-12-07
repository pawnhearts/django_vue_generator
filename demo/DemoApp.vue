<template>
  <div id="app">
    <BookList></BookList>
    <BookForm :pk="1" @success="on_success"></BookForm>
  </div>
</template>

<script>
import BookForm from "./components/BookForm";
import BookList from "./components/BookList";

export default {
  name: 'app',
  components: {
    BookForm,
    BookList
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
