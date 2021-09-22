<template>
    <h3>Para adicionar um site, preencha abaixo:</h3>
    <form>
        <label for="cfsProfile">Para qual lista deseja a liberação?</label> <br>
        <select name=cfsListNames id="cfsListNames">
            <option></option>
        </select> <br>

        <label for="uriToAdd">Qual o domínio do site a ser liberado?</label> <br>
        <input v-model="uriToAdd" type="text" name="uriToAdd" id="uriToAdd" placeholder="infomach.com.br"> <br>
        <button>Adicionar</button>
    </form>
</template>

<script setup>
    import { ref } from 'vue'
    const uriToAdd = ref('')
</script>