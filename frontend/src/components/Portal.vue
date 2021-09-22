<template>
    <h1>Bem vindo!</h1>
    <h2>Você está conectado no firewall {{currentFwName}}</h2>
    <h3>O que gostaria de fazer?</h3>

    <a href="/addtolist">
        <button>Liberar site</button>
    </a>

    <a href="/removefromlist">
        <button>Remover site</button>
    </a>
</template>

<script setup>
    import { ref } from 'vue'
    import axios from 'axios'
    const currentFwName = ref('')

    const getCFSLists = async () => {
        axios.get('http://172.21.81.234:5000/showcfslists')
    }
    const response = getCFSLists()
    console.log(response)

</script>

