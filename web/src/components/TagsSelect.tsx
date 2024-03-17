import { CreatableSelect, useChakraSelectProps } from 'chakra-react-select';
import { forwardRef, useEffect, useMemo, useState } from 'react';

function TagsSelect({ value, onChange, ...props }: any, ref: any) {
    const [selectedOptions, setSelectedOptions] = useState([]);

    const handleChange = (options: any) => {
        setSelectedOptions(options);
        if (onChange && options) {
            onChange({
                target: {
                    name: props.name,
                    value: options.map((o: any) => o.value).join("\n")
                }
            });
        }
    };

    const options = useMemo(() => {
        const tags = value ? value.split("\n") : [];
        return tags.map((t: any) => { return { value: t, label: t } });
    }, [value]);

    useEffect(() => {
        setSelectedOptions(options);
    }, [value]);

    const selectProps = useChakraSelectProps<any, true>({
        isMulti: true,
        isClearable: true,
        options: options,
        onChange: handleChange,
        value: selectedOptions,
        placeholder: "Select or create tags..."
    });

    return (
        <CreatableSelect
            ref={ref}
            {...selectProps}
        />
    );
}

export default forwardRef(TagsSelect);