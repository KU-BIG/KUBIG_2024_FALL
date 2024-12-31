import { NextResponse } from "next/server";
import bcrypt from "bcrypt";
import prismadb from "@/lib/prismadb";

export async function POST(req: Request) {
    console.log("API 호출됨");

    try {
        const { email, password } = await req.json();

        console.log("email", email);
        console.log("password", password);

        // 이메일 중복 확인
        const existingUser = await prismadb.user.findUnique({
            where: { email },
        });

        console.log("existingUser", existingUser);

        if (existingUser) {
            return NextResponse.json(
                { error: "이미 존재하는 이메일입니다." },
                { status: 400 }
            );
        }

        // 비밀번호 암호화
        const hashedPassword = await bcrypt.hash(password, 10);

        // 새로운 사용자 생성
        const newUser = await prismadb.user.create({
            data: {
                email,
                password: hashedPassword,
            },
        });

        console.log("this is USer", newUser)

        return NextResponse.json({
            id: newUser.id,
            email: newUser.email,
        });
    } catch (error) {
        console.error(error);
        return NextResponse.json(
            { error: "회원가입 처리 중 오류가 발생했습니다." },
            { status: 500 }
        );
    }
}
