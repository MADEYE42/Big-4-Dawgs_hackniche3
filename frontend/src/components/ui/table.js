import React from "react";

export function Table({ children, className }) {
  return (
    <div className={`overflow-x-auto rounded-lg shadow-md ${className} font-[Poppins]`}>
      <table className="min-w-full bg-white border border-gray-300 rounded-lg">
        {children}
      </table>
    </div>
  );
}

export function TableHeader({ children, className }) {
  return (
    <thead className={`bg-gray-300 text-white text-left ${className}`}>
      {children}
    </thead>
  );
}

export function TableRow({ children, className }) {
  return (
    <tr className={`border-b hover:bg-gray-100 transition duration-200 ${className}`}>
      {children}
    </tr>
  );
}

export function TableCell({ children, className }) {
  return (
    <td className={`p-4 border text-gray-700 ${className}`}>
      {children}
    </td>
  );
}

export function TableBody({ children, className }) {
  return <tbody className="divide-y divide-gray-200">{children}</tbody>;
}
