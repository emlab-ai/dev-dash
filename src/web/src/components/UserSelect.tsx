import { Box } from "@chakra-ui/react";
import { useOrgProviderContext } from "@src/providers/orgProvider";
import { Select, useChakraSelectProps } from 'chakra-react-select';
import { forwardRef, useCallback, useEffect, useMemo, useState } from "react";

export default forwardRef(function UserSelect({ excludeId, isManager, ...props }: any, ref: any) {
    const { users } = useOrgProviderContext();
    const filteredUsers = users.filter(u => {
        return excludeId !== u.id && (!!isManager === !!u.isManager);
    });

    const options = useMemo(() => {
        return filteredUsers.map(t => ({ label: t.name, value: t.id }))
    }, [users])

    const currentOption = options.filter(o => o.value === props.value);

    const [selectedOptions, setSelectedOptions] = useState<any>(currentOption);
    useEffect(() => {
        setSelectedOptions(currentOption);
    }, [props.value]);

    const onChange = useCallback((value:any) => {
        setSelectedOptions(value);
        if (props.onChange) {
            props.onChange({
                target: {
                    name: props.name,
                    value: value?.value
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
            <Select ref={ref} {...selectProps} 
                size={props.size} 
                options={options} 
                chakraStyles={{
                    menu: (provided) => ({
                      ...provided,
                      zIndex: 9999, 
                    }),
                  }}
                />
        </Box>
    )
})