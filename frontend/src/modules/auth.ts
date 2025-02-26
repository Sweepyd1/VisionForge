import axios from "axios";
import { err_popup } from "@/modules/swal2";
import { router } from "@/router";


export async function login(username: string, password: string): Promise<string> {
	return axios.post("/api/auth/login", {username: username, password: password})
        .then(response => { router.push("/") })
        .catch(err => {
           return err.response.data.detail || "Не удалось соединиться с сервером..."
        })
}

export async function registration(email: string, username: string, password: string, name: string): Promise<string> {
	return axios.post(
		"/api/auth/register",
		{email: email, username: username, password: password, name: name}
	)
        .then(response => { router.push("/") })
        .catch(err => {
            return err.response.data.detail || "Не удалось соединиться с сервером..."
        })
}

export async function isAuthenticated(): Promise<boolean> {
	return axios.post("/api/auth/is_authenticated")
		.then(response => { return true })
		.catch(e => { return false });
}

export function logout() {
	axios.post("/api/auth/logout")
		.then(response => { router.push("/auth/login") })
		.catch(e => { err_popup("Не удалось выйти...") });
}
