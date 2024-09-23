<script setup>
import {onMounted, ref} from "vue";
import {login, isAuthenticated} from "@/modules/auth";
import { router } from "@/router/index";

const username = ref('')
const password = ref('')
const errors = ref([])

async function auth() { 
	errors.value = []
	const err = await login(username.value, password.value)
	if (err) {
		errors.value.push(err)
	}
}

onMounted(async () => {
	if (await isAuthenticated()) {
		router.push("/");
	}
})
</script>

<template>
	<div class="bg">
		<div class="auth-container">
			<div class="block">
				<p class="title">Авторизация</p>
				<input placeholder="Логин" v-model="username">
				<input placeholder="Пароль" v-model="password">
			</div>

			<div class="block">
				<button class="auth-btn" @click="auth">Войти</button>
				<p v-for="err in errors" class="errors">{{err}}</p>
				<router-link to="/auth/registration" class="another-way">Еще не зарегестрированы?</router-link>
			</div>
		</div>
	</div>
</template>

<style scoped lang="scss">
.bg {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100vh;
}

.auth-container {
	background: var(--sbg);
	width: 80%;
	max-width: 600px;
	border-radius: 15px;
	padding: 15px 0 20px;
	box-sizing: border-box;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}

.block {
	width: 100%;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.title {
	font-size: 23px;
	font-weight: 700;
	margin-bottom: 30px;
	color: var(--text)
}

.auth-container input {
	background: var(--light-sbg);
	width: 90%;
	height: 60px;
	border-radius: 15px;
	border: none;
	padding-left: 10px;
	box-sizing: border-box;
	color: var(--text);
	font-weight: 600;
	font-size: 16px;
	outline: none;
	margin-bottom: 15px;
}

.auth-container input::placeholder {
	color: var(--button);
}

.errors {
	color: red;
	margin-bottom: 0;
}

.auth-btn {
	background: var(--button);
	border-radius: 15px;
	border: none;
	width: 90%;
	height: 60px;
	color: var(--text);
	font-weight: 600;
	font-size: 18px;
}

.another-way {
	color: var(--button);
	font-size: 14px;
	font-weight: 600;
	text-decoration: none;
	margin-top: 10px;
}
</style>
