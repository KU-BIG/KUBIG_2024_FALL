import { NextRequest, NextResponse } from "next/server";
import prismadb from "@/lib/prismadb";
import { getUserIdFromRequest } from "@/lib/auth";

// 특정 채팅방 조회
export async function GET(
    req: NextRequest,
    { params }: { params: { chatroomId: string } }
) {
    try {
        console.log("chatroomid get 호출됨")

        const { chatroomId } = await params;

        if (!chatroomId) {
            return NextResponse.json(
                { error: "Chatroom ID is required" },
                { status: 400 }
            );
        }

        const userId = getUserIdFromRequest(req);

        if (!userId) {
            return NextResponse.json(
                { error: "사용자 인증이 필요합니다." },
                { status: 401 }
            );
        }

        const chatroom = await prismadb.chatRoom.findUnique({
            where: { id: chatroomId },
            include: {
                messages: { orderBy: { createdAt: "asc" } }, // 채팅 메시지 포함
            },
        });

        if (!chatroom || chatroom.userId !== userId) {
            return NextResponse.json(
                { error: "접근 권한이 없습니다." },
                { status: 403 }
            );
        }

        // 채팅방이 없을 경우 404 반환
        if (!chatroom) {
            return NextResponse.json(
                { error: "Chatroom not found" },
                { status: 404 }
            );
        }

        return NextResponse.json(chatroom);
    } catch (error) {
        console.error("Error fetching chatroom:", error);
        return NextResponse.json(
            { error: "Failed to fetch chatroom" },
            { status: 500 }
        );
    }
}

// 특정 채팅방 삭제
export async function DELETE(
    req: NextRequest,
    { params }: { params: { chatroomId: string } }
) {
    console.log("chat delete!");
    try {
        const { chatroomId } = await params;

        if (!chatroomId) {
            return NextResponse.json(
                { error: "Chatroom ID is required" },
                { status: 400 }
            );
        }

        const userId = getUserIdFromRequest(req);

        if (!userId) {
            return NextResponse.json(
                { error: "사용자 인증이 필요합니다." },
                { status: 401 }
            );
        }

        const chatRoom = await prismadb.chatRoom.findUnique({
            where: { id: chatroomId },
        });

        if (!chatRoom || chatRoom.userId !== userId) {
            return NextResponse.json(
                { error: "삭제 권한이 없습니다." },
                { status: 403 }
            );
        }

        await prismadb.chatRoom.delete({
            where: { id: chatroomId },
        });

        return NextResponse.json({ message: "Chatroom deleted successfully" });
    } catch (error) {
        console.error("Error deleting chatroom:", error);
        return NextResponse.json(
            { error: "Failed to delete chatroom" },
            { status: 500 }
        );
    }
}

// 채팅방 이름 수정

export async function PATCH(
    req: NextRequest,
    { params }: { params: { chatroomId: string } }
) {
    try {
        console.log("chatroomid patch 호출됨")

        const { chatroomId } = await params;

        if (!chatroomId) {
            return NextResponse.json(
                { error: "Chatroom ID is required" },
                { status: 400 }
            );
        }

        const body = await req.json();
        const name = body?.name;

        if (!name) {
            return NextResponse.json(
                { error: "Name is required" },
                { status: 400 }
            );
        }

        const updatedChatroom = await prismadb.chatRoom.update({
            where: { id: chatroomId },
            data: { name },
        });

        return NextResponse.json(updatedChatroom);
    } catch (error) {
        console.error("Error updating chatroom:", "details:", error);

        return NextResponse.json(
            { error: "Failed to update chatroom" },
            { status: 500 }
        );
    }
}
