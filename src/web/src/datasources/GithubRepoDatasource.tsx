import { useAxiosClient } from "@src/clients/backendClient";
import { GithubRepo } from "@src/model";
import { useCallback, useEffect, useState } from "react";

export const useGithubRepoDatasource = () => {
    const [repos, setRepos] = useState<GithubRepo[]>([]);
    const [reposBefore, setReposBefore] = useState<string|null>(null);
    const [reposAfter, setReposAfter] = useState<string|null>(null);
    const [filter, setFilter] = useState<string>("");
    const axiosFetch = useAxiosClient();

    const fetchReposAsync = useCallback(async (before?: string, after?: string, filter?: string) => {
        try {
            let pageStr = '';
            if (before) {
                pageStr = `&before=${before}`;
            } else if (!after) {
                pageStr = `&after=${after}`;
            } 
            if (filter) {
                pageStr += `&filter=${filter}`;
            }

            const response = await axiosFetch(`/api/repoSettings?page_size=100${pageStr}`);
            const result = await response.data;

            setRepos(result.data);
            setReposBefore(result.before);
            setReposAfter(result.after);
        } catch (error) {
            console.error('Error fetching reviews', error);
        }
    }, [axiosFetch]);


    useEffect(() => {
        fetchReposAsync();
    }, [fetchReposAsync]);

    useEffect(() => {
        fetchReposAsync(undefined, undefined, filter);
    }, [filter, fetchReposAsync]);
   
    const nextPage = useCallback(async () => {
        if (!reposAfter) {
            return;
        }
        fetchReposAsync(undefined, reposAfter);
    }, [reposAfter, fetchReposAsync]);

    const prevPage = useCallback(async () => {
        if (!reposBefore) {
            return;
        }
        fetchReposAsync(reposBefore);
    }, [reposBefore, fetchReposAsync]);

    return {
        repos,
        setFilter,
        nextPage,
        prevPage,
        reposBefore,
        reposAfter
    }
}