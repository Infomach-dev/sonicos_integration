<template>
    <form>
        <label for="fwUser">Usuário</label>
        <br />
        <input v-model="username" type="text" name="fwUser" id="fwUser" required />
        <br />
        <br />
        <label for="fwPassword">Senha</label>
        <br />
        <input v-model="password" type="password" name="fwPassword" id="fwPassword" required />
        <br />
        <br />
        <p v-if="errorMessage">{{ errorMessage }}</p>
        <p v-if="loading">Carregando...</p>
        <button :disabled="loading" @click.prevent="loginOnPortal">Logar</button>
    </form>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { Appwrite } from "appwrite"

const api = new Appwrite()
api
    .setEndpoint('http://localhost/v1') // Your Appwrite Endpoint
    .setProject('613f9ccf42af1') // Your project ID

const username = ref("")
const password = ref("")
const errorMessage = ref("")
const loading = ref(false)

const loginOnPortal = async () => {
    loading.value = true

    try {
        errorMessage.value = ""
        const response = await api.account.createSession(username.value, password.value)
        console.log(response)
        getDocument()
        // loginOnFw()

    } catch (error) {
        errorMessage.value = error.message
    }
    loading.value = false
}

const getDocument = async () => {
    const response = await api.database.listDocuments('6142561adbd8e')
    console.log(response)
}

const loginOnFw = async () => {
    let formData = new FormData()
    formData.append('fwAddress', 'https://l2.security.infomach.com.br:6443')
    formData.append('fwUser', 'joaolima')
    formData.append('fwPassword', 'F@C3Ce6jluK6(lzK')

    const response = axios.post('http://172.21.81.234:5000/login', formData)
        .then(function (response) {
            console.log(response);
        })
        .catch(function (error) {
            console.log(error);
        });
}

</script>