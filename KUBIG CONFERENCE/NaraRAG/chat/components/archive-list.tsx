"use client";

import { useEffect, useState } from "react";
import ArchiveMessage from "./archive-message";

interface ArchivedMessage {
    id: string;
    content: string;
    createdAt: string;
    chatroomName: string;
    userId: string
}

const ArchiveList = () => {
    const [archivedMessages, setArchivedMessages] = useState<ArchivedMessage[]>(
        []
    );

    useEffect(() => {
        const fetchArchivedMessages = async () => {
            try {
                const response = await fetch("/api/archive");
                if (!response.ok) {
                    throw new Error("Failed to fetch archived messages");
                }

                const data = await response.json();
                setArchivedMessages(data);
            } catch (error) {
                console.error("Error fetching archived messages:", error);
            }
        };

        fetchArchivedMessages();
    }, []);

    const handleDelete = (messageId: string) => {
        setArchivedMessages((prev) =>
            prev.filter((message) => message.id !== messageId)
        );
    };

    return (
        <div className="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-5">
            {archivedMessages.map((message) => (
                <ArchiveMessage
                    key={message.id}
                    content={message.content}
                    chatroomName={message.chatroomName}
                    createdAt={message.createdAt}
                    messageId={message.id}
                    onDelete={handleDelete}
                />
            ))}
        </div>
    );
};

export default ArchiveList;
