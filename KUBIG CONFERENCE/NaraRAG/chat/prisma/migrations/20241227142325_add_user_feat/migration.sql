-- DropForeignKey
ALTER TABLE "ArchivedMessage" DROP CONSTRAINT "ArchivedMessage_chatroomId_fkey";

-- DropForeignKey
ALTER TABLE "Message" DROP CONSTRAINT "Message_userId_fkey";
