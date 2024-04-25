import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export function useSearchStateParams(param: string, defaultValue?: string): [string, Dispatch<SetStateAction<string>>] {
    const searchParams = new URLSearchParams(location.search);
    const [value, setValue] = useState(searchParams.get(param) as string | undefined ?? defaultValue ?? "");
    const navigate = useNavigate();

    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);

        if (value && value !== defaultValue) {
            searchParams.set(param, value);
        } else {
            searchParams.delete(param);
        }

        navigate({
            pathname: location.pathname,
            search: searchParams.toString(),
        });
    }, [value, navigate]);

    return [value, setValue] as [string, Dispatch<SetStateAction<string>>];

}
