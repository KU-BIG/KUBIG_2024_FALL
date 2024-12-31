"use client";

import { toast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

export default function SignupPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [emailError, setEmailError] = useState("");
    const [passwordError, setPasswordError] = useState("");

    const router = useRouter();

    const handleSignup = async () => {
        if (!email || !password) {
            setMessage("이메일과 비밀번호를 모두 입력해주세요.");
            return;
        }

        if (!validateEmail(email)) {
            setEmailError("유효한 이메일을 입력해주세요.");
            return;
        } else {
            setEmailError("");
        }

        if (password.length < 8) {
            setPasswordError("비밀번호는 8자 이상이어야 합니다.");
            return;
        } else {
            setPasswordError("");
        }

        try {
            console.log("요청 데이터:", { email, password });

            const response = await fetch("/api/auth/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                try {
                    const data = await response.json();
                    setMessage(data.error || "회원가입 실패");
                } catch {
                    setMessage("회원가입 실패");
                }
                return;
            }

            const data = await response.json();
            toast({ title: "회원가입 성공!", description: "로그인 해주세요." });

            router.push("/");
        } catch (error) {
            setMessage("회원가입 중 오류가 발생했습니다.");
            console.error(error);
        }
    };

    const validateEmail = (email: string) => {
        const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(email);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-[#c2dbf9] to-[#87bdff]">
            <div className="bg-white p-8 rounded-lg shadow-lg w-[450] h-[390px] ">
                <h1 className="text-2xl font-bold mb-6 text-center">
                    Sign Up to Nararag
                </h1>
                <div className="px-2 mt-5 flex flex-col align-middle items-center justify-between">
                    <li className="text-[15px]" >채팅방, 아카이브 저장은 로그인 후에만 가능해요!</li>
                </div>
                <div className=" pt-9 mb-4">
                    <input
                        type="email"
                        placeholder="이메일"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full p-3 border rounded-lg"
                    />
                    {emailError && (
                        <p className="text-red-500 text-sm">{emailError}</p>
                    )}
                </div>
                <div className="mb-10">
                    <input
                        type="password"
                        placeholder="비밀번호"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-3 border rounded-lg"
                    />
                    {passwordError && (
                        <p className="text-red-500 text-sm">{passwordError}</p>
                    )}
                </div>
                <button
                    onClick={handleSignup}
                    className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-400"
                >
                    회원가입
                </button>
                {message && (
                    <p className="mt-4 text-center text-red-500">{message}</p>
                )}
            </div>
        </div>
    );
}
