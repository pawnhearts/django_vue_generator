<template>
  <div id="app">
    <select name="state" v-model="filters.state">
      <option value="">Any</option>
      <option value="published">Published</option>
      <option value="not_published">Not published</option>
      <option value="in_progress">In progress</option>
      <option value="cancelled">Cancelled</option>
      <option value="rejected">Rejected</option>
    </select>
    <BookList :filters="filters"></BookList>
      <hr/>
    <AuthorList>
      <template v-slot:header><th>Name</th></template>
      <template v-slot:object="{object}"><td>{{object.name}}<br/><ul><li v-for="book in object.books" :key="book.id">{{book.title}}</li></ul></td></template>
    </AuthorList>
      <hr/>
    <BookForm :pk="1" @success="on_success"></BookForm>
  </div>
</template>

<script>
import BookForm from "./components/BookForm";
import BookList from "./components/BookList";
import AuthorList from "./components/AuthorList";

export default {
  name: 'app',
  components: {
    BookForm,
    BookList,
    AuthorList
  },
  data() {
    return {
      filters: {'state': ''}
    }
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
