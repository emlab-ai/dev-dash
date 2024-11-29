/* eslint-disable @typescript-eslint/no-explicit-any */
import { useCallback, useRef, useEffect } from 'react';

type AnyFunction = (...args: any[]) => any;

export function useDebounceCallback<T extends AnyFunction>(
  callback: T,
  delay: number,
  dependencies: any[]
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const debouncedCallback = useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [delay, callback, ...dependencies]) as T;

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return debouncedCallback;
}

export default useDebounceCallback;