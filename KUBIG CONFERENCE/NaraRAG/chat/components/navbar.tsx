"use client";

import React, { useEffect, useMemo, useState } from "react";
import MobileSidebar from "./mobile-sidebar";
import { ChatRoom } from "@prisma/client";
import Image from "next/image";
import { redirect, usePathname } from "next/navigation";
import LoginModal from "./login-modal";

interface NavBarProps {
    chatrooms: ChatRoom[];
    createChatroom: () => void;
    deleteChatroom: (id: string) => void;
    renameChatroom: (id: string, newName: string) => void;
}

const NavBar: React.FC<NavBarProps> = ({
    chatrooms,
    createChatroom,
    deleteChatroom,
    renameChatroom,
}) => {
    const pathname = usePathname();
    const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // 현재 경로에서 chatroomId 추출
    const activeChatroomName = useMemo(() => {
        const match = pathname?.match(/\/chat\/([\w-]+)/); // 경로에서 '/chat/:id' 추출
        const chatroomId = match ? match[1] : null;

        // chatrooms 배열에서 현재 chatroomId에 해당하는 채팅방 이름 찾기
        const activeChatroom = chatrooms.find(
            (chatroom) => chatroom.id === chatroomId
        );
        return activeChatroom ? activeChatroom.name : "";
    }, [pathname, chatrooms]);

    // 로그인 상태 확인
    useEffect(() => {
        const token = localStorage.getItem("token");
        setIsLoggedIn(!!token); // 토큰이 존재하면 로그인 상태로 설정
    }, []);

    // 로그아웃 처리
    const handleLogout = () => {
        localStorage.removeItem("token"); // 로컬 스토리지에서 토큰 제거
        setIsLoggedIn(false); // 상태를 로그아웃 상태로 설정
        redirect("/"); // 메인 페이지로 리다이렉트
    };

    return (
        <div
            className="fixed w-full flex  border-b bg-gray-50 px-3 pt-2 pb-4 rounded-b-[15]"
            style={{
                boxShadow: `0 1.2px 3px 0 rgba(0,0,0,0.2)`,
            }}
        >
            <div className="flex relative items-center w-full mx-auto px-1">
                <div className="pt-2 px-2">
                    <MobileSidebar
                        chatrooms={chatrooms}
                        createChatroom={createChatroom}
                        deleteChatroom={deleteChatroom}
                        renameChatroom={renameChatroom}
                    />
                </div>

                <button
                    className="flex-1 flex justify-center md:justify-start"
                    onClick={() => window.location.replace("/")}
                >
                    <div className="flex items-center">
                        <Image
                            src="/images/nararag-logo.png"
                            alt="NaraRAG"
                            width={70}
                            height={100}
                        />
                    </div>
                </button>

                <div className="hidden md:flex absolute left-1/2 transform -translate-x-1/2 text-[20px] pt-2">
                    {activeChatroomName || ""}
                </div>

                {isLoggedIn ? (
                    <button
                        className="absolute right-8 pt-1"
                        onClick={handleLogout}
                    >
                        Logout
                    </button>
                ) : (
                    <button
                        className="absolute right-8 pt-3"
                        onClick={() => setIsLoginModalOpen(true)}
                    >
                        Login
                    </button>
                )}

                <LoginModal
                    isOpen={isLoginModalOpen}
                    onClose={() => setIsLoginModalOpen(false)}
                    onLoginSuccess={() => setIsLoggedIn(true)}
                />
            </div>
        </div>
    );
};

export default NavBar;
