import { NextRequest, NextResponse } from "next/server";
import prismadb from "@/lib/prismadb";
import { ChatRoom } from "@prisma/client";
import { getUserIdFromRequest } from "@/lib/auth";

// 채팅방 목록 조회
export async function GET(req: NextRequest) {
    try {
        console.log("chatlist get 호출됨")

        const userId = getUserIdFromRequest(req);

        if (!userId) {
            return NextResponse.json(
                { error: "사용자 인증이 필요합니다." },
                { status: 401 }
            );
        }

        const chatRooms: ChatRoom[] = await prismadb.chatRoom.findMany({
            where: { userId },
            orderBy: { createdAt: "desc" },
        });

        return NextResponse.json(chatRooms);
    } catch (error) {
        console.error("Error fetching chatrooms:", error);
        return NextResponse.json(
            { error: "Failed to fetch chatrooms" },
            { status: 500 }
        );
    }
}

// 새로운 채팅방 생성
export async function POST(req: NextRequest) {
    console.log(" create cahtroom API 호출됨");
    console.log("Authorization Header:", req.headers.get("Authorization"));

    try {
        const userId = getUserIdFromRequest(req);

        if (!userId) {
            return NextResponse.json(
                { error: "사용자 인증이 필요합니다." },
                { status: 401 }
            );
        }

        const body = await req.json();
        const name = body?.name || "New Chat Room";

        const chatRoom = await prismadb.chatRoom.create({
            data: { name, userId },
        });

        return NextResponse.json(chatRoom);
    } catch (error) {
        console.error("Error creating chatroom:", error);
        return NextResponse.json(
            { error: "Failed to create chatroom" },
            { status: 500 }
        );
    }
}
