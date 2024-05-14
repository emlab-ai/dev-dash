import { Box } from "@chakra-ui/react";
import { useOrgProviderContext } from "@src/providers/orgProvider";
import { Select, useChakraSelectProps } from 'chakra-react-select';
import { forwardRef, useCallback, useEffect, useMemo, useState } from "react";

export default forwardRef(function UserSelect({ excludeId, isManager, ...props }: any, ref: any) {
    const { gitUsers } = useOrgProviderContext();

    const options = useMemo(() => {
        return gitUsers.map(t => ({ label: t.login, value: t.id }))
    }, [gitUsers])

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
        isClearable: true,
        value: selectedOptions,
        onChange: onChange       
    });

    return (
        <Box { ...props}>
            <Select ref={ref} {...selectProps} size={props.size} options={options} />
        </Box>
    )
})