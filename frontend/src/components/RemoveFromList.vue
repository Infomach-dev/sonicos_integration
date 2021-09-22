<template>
    <h3>Para remover um site já liberado, preencha abaixo:</h3>
    <form method="POST" action="/removefromlist">
        <label for="cfsProfile">Qual a lista contém o site a ser removido?</label> <br>
        <select name=cfsListName id="cfsListName">
            <option></option>
        </select> <br>

        <label for="uriToDel">Qual o domínio do site a ser removido?</label> <br>
        <input v-model="uriToDel" type="text" name="uriToDel" id="uriToDel" placeholder="infomach.com.br"> <br>
        <button>Remover</button>
    </form>
</template>

<script setup>
    import { ref } from 'vue'
    const uriToDel = ref('')
</script>