import { useOrgProviderContext } from "@src/providers/orgProvider";
import { Select , useChakraSelectProps} from 'chakra-react-select';
import { forwardRef, useCallback, useEffect, useMemo, useState } from "react";

export default forwardRef(function TeamSelect({excludeId, ...props}: any, ref:any) {
    const { teams } = useOrgProviderContext();

    const filteredTeams = useMemo(()=>teams.filter(u => {
        return excludeId !== u.id;
    }), [teams]);

    const options = useMemo(() => {
        return filteredTeams.map(t => ({ label: t.name, value: t.id }))
    }, [filteredTeams])

    const currentOption = options.filter(o => o.value === props.value);
    const [selectedOptions, setSelectedOptions] = useState<any>(currentOption);
    
    useEffect(() => {
        setSelectedOptions(currentOption);
    }, [props.value]);

    const onChange = useCallback((value:any) => {
        setSelectedOptions(value);
        if (props.onChange && value) {
            props.onChange({
                target: {
                    name: props.name,
                    value: value.value
                }
            });
        }
    }, [setSelectedOptions]);

    const selectProps = useChakraSelectProps({
        isMulti: false,
        value: selectedOptions,
        onChange: onChange,
    });

    return (
        <Select ref={ref} {...selectProps} options={options} />
    )
})