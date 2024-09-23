<template>
  <router-view/>
</template>

<style lang="scss">
:root {
    --bg: #eff1f5;
    --dark-sbg: #9ca0b0;
    --sbg: #bcc0cc;
    --light-sbg: #ccd0da;
	--button: #7287fd;
	--hint: #FFFFFF70; 
    --text: #4c4f69;

	text-rendering: optimizeLegibility;
	-webkit-font-smoothing: antialiased;
	-webkit-text-size-adjust: 100%;
	font-family: 'Montserrat', sans-serif;
}

body {
	background: var(--bg);
	color: var(--text);
	margin: 0;
}
</style>
