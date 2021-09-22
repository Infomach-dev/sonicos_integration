<template>
  <input v-model="activeComponent" type="radio" id="loginRadio" value="login" />
  <label for="loginRadio">Login</label>
  <input v-model="activeComponent" type="radio" id="portalRadio" value="portal" />
  <label for="portalRadio">Portal</label>
  <input v-model="activeComponent" type="radio" id="addToListRadio" value="addtolist" />
  <label for="portalRadio">AddToList</label>
  <input v-model="activeComponent" type="radio" id="removeFromListRadio" value="removefromlist" />
  <label for="portalRadio">RemoveFromList</label>



  <VLogin v-if="activeComponent === 'login'" />
  <VPortal v-if="activeComponent === 'portal'" />
  <VAddToList v-if="activeComponent === 'addtolist'" />
  <VRemoveFromList v-if="activeComponent === 'removefromlist'" />

</template>

<script setup>
import { ref } from 'vue';
import VLogin from './components/Login.vue'
import VPortal from './components/Portal.vue'
import VAddToList from './components/AddToList.vue'
import VRemoveFromList from './components/RemoveFromList.vue'

const activeComponent = ref("login")
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
