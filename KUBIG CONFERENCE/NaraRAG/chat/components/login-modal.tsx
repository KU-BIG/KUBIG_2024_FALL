"use client";

import React, { useState } from "react";
import ReactDOM from "react-dom";
import { useToast } from "@/hooks/use-toast";

interface LoginModalProps {
    isOpen: boolean;
    onClose: () => void;
    onLoginSuccess: (userData: { email: string }) => void; // 로그인 성공 시 데이터를 전달
}

const LoginModal: React.FC<LoginModalProps> = ({
    isOpen,
    onClose,
    onLoginSuccess,
}) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const { toast } = useToast();

    if (!isOpen) return null;

    const handleLogin = async () => {
        setError(""); // 에러 초기화
        if (!email || !password) {
            setError("이메일과 비밀번호를 입력하세요.");
            return;
        }

        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const data = await response.json();
                setError(data.error || "로그인 실패");
                return;
            }

            const userData = await response.json(); // 로그인 성공 시 유저 데이터를 받음
            console.log("userData", userData);
            localStorage.setItem("token", userData.token); // 토큰을 로컬스토리지에 저장

            toast({ description: "로그인 성공!" });

            // 상위 컴포넌트에 유저 데이터 전달
            onLoginSuccess(userData); // 상위 컴포넌트에 유저 데이터 전달
            onClose();
        } catch (error) {
            setError("로그인 중 오류가 발생했습니다.");
            console.error(error);
        }
    };

    const modalContent = (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-gray-800 bg-opacity-50">
            <div className="bg-white p-6 rounded shadow-lg w-[400px]">
                <h2 className="text-lg font-semibold mb-4">로그인</h2>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="이메일"
                    className="w-full p-2 border rounded mb-4"
                />
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="비밀번호"
                    className="w-full p-2 border rounded mb-4"
                />
                {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
                <div className="flex flex-col items-center gap-2">
                    <button
                        onClick={handleLogin}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 w-[300]"
                    >
                        로그인
                    </button>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 w-[300]"
                    >
                        닫기
                    </button>
                </div>
                <div className="mt-4 text-center">
                    <a
                        href="/sign-up"
                        className="text-blue-500 hover:underline"
                    >
                        회원가입
                    </a>
                </div>
            </div>
        </div>
    );

    return ReactDOM.createPortal(modalContent, document.body); // Modal을 body 아래 렌더링
};

export default LoginModal;
