"use client";

import React, { useEffect } from "react";
import NavBar from "./navbar";
import SideBar from "./sidebar";

import { useRouter } from "next/navigation";
import { useChatroomStore } from "@/store/chatroomStore";

const Bars = () => {
    const router = useRouter();
    const {
        chatrooms,
        fetchChatrooms,
        createChatroom,
        deleteChatroom,
        renameChatroom,
    } = useChatroomStore();

    useEffect(() => {
        fetchChatrooms();

        window.addEventListener("storage", (event) => {
            if (event.key === "token") {
                fetchChatrooms();
            }
        });

        return () => {
            window.removeEventListener("storage", () => {});
        };
    }, [fetchChatrooms]);

    const handleCreateChatroom = () => createChatroom(router);
    const handleDeleteChatroom = (id: string) => deleteChatroom(id, router);
    const handleRenameChatroom = (id: string, newName: string) =>
        renameChatroom(id, newName);

    return (
        <div className="z-10">
            <div className="fixed">
                <NavBar
                    chatrooms={chatrooms}
                    createChatroom={handleCreateChatroom}
                    deleteChatroom={handleDeleteChatroom}
                    renameChatroom={handleRenameChatroom}
                />
            </div>

            <div className="mt-[72px] fixed inset-y-0">
                <SideBar
                    chatrooms={chatrooms}
                    createChatroom={handleCreateChatroom}
                    deleteChatroom={handleDeleteChatroom}
                    renameChatroom={handleRenameChatroom}
                />
            </div>
        </div>
    );
};

export default Bars;
