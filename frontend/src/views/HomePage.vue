<script lang="ts" setup>
import { logout } from "@/modules/auth";
</script>

<template>
  <div class="home">
	<h1 class="title">Welcome to INNO-HACK</h1>
	<p class="description">You have been successfully authorized</p>
	<button @click="logout" class="logout">logout</button>
  </div>
</template>

<style scoped lang="scss">
.home {
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	height: 100vh;
	width: 100%;

	.title {
		margin-bottom: 0;
	}

	.description {
		margin-bottom: 30px;
		color: var(--text);
	}

	.logout {
		background: var(--button);
		border-radius: 15px;
		border: none;
		width: 40%;
		max-width: 500;
		height: 60px;
		color: var(--text);
		font-weight: 600;
		font-size: 18px;
	}
}

</style>