import prismadb from "@/lib/prismadb";
import { NextRequest, NextResponse } from "next/server";

export async function DELETE(
    req: NextRequest,
    { params }: { params: { messageId: string } }
) {
    console.log("Deleting message");
    try {
        const { messageId } = await params;

        if (!messageId) {
            return NextResponse.json(
                { error: "Message ID is required" },
                { status: 400 }
            );
        }

        // Prisma를 사용해 데이터베이스에서 메시지 삭제
        await prismadb.archivedMessage.delete({
            where: { id: messageId },
        });

        return NextResponse.json(
            { message: "Message deleted successfully" },
            { status: 200 }
        );
    } catch (error) {
        console.error("Error deleting message:", error);
        return NextResponse.json(
            { error: "Failed to delete message" },
            { status: 500 }
        );
    }
}
