import React from 'react';


// Placeholder components for the chat UI
const Header = () => (
  <header className="bg-green-800 text-white p-4 text-center">
    <h1 className="text-2xl font-bold">Wellchemy</h1>
  </header>
);


const LeftRail = () => (
  <div className="bg-green-100 p-4 h-full">
    <h2 className="text-lg font-semibold mb-2">Chat History</h2>
    <ul className="space-y-2">
      <li className="p-2 bg-green-200 rounded">Chat 1</li>
      <li className="p-2 bg-green-200 rounded">Chat 2</li>
      <li className="p-2 bg-green-200 rounded">Chat 3</li>
    </ul>
  </div>
);


const ChatArea = () => (
  <div className="flex flex-col h-full">
    <div className="flex-1 p-4 overflow-y-auto bg-green-50">
      <div className="mb-4 p-3 bg-green-200 rounded-lg">Hello! How can I help you today?</div>
      <div className="mb-4 p-3 bg-green-200 rounded-lg">I'm here to assist with your dietary needs.</div>
    </div>
    <div className="p-4 border-t border-green-300">
      <div className="flex">
        <input
          type="text"
          placeholder="Type your message..."
          className="flex-1 p-2 border border-green-300 rounded-l"
        />
        <button className="bg-green-800 text-white p-2 rounded-r">Send</button>
      </div>
    </div>
  </div>
);


const Footer = () => (
  <footer className="bg-green-800 text-white p-4 text-center">
    <p>© 2023 Wellchemy. All rights reserved.</p>
  </footer>
);


export default function Home() {
  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1">
        <div className="w-1/4">
          <LeftRail />
        </div>
        <div className="w-3/4">
          <ChatArea />
        </div>
      </div>
      <Footer />
    </div>
  );
}
