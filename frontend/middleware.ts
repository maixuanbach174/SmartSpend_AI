import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/login', '/_next', '/favicon.ico', '/logo.svg'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // If the request is for a public file or route, skip auth
  if (PUBLIC_PATHS.some(path => pathname.startsWith(path))) {
    return NextResponse.next();
  }

  // Check token in cookies or localStorage (note: middleware can't access localStorage)
  const token = request.cookies.get('access_token')?.value;

  // If token not found, redirect to login
  if (!token) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next|favicon.ico|logo.svg).*)'], // Protect all routes except assets
};
