import { Button, ButtonGroup } from "@chakra-ui/react";
import { useEffect, useState } from "react";

const dateOptions = [
    { label: '12m', value: '12months' },
    { label: '6m', value: '6months' },
    { label: '1m', value: '1month' },
    { label: '14d', value: '14days' },
  ];
  
const DateFilterToggle = ({ value, onChange, size }: any) => {
    const [selected, setSelected] = useState(value);
    useEffect(() => {
      setSelected(value);
    }, [value]);
  
    const handleClick = (value: any) => {
      setSelected(value);
      if (onChange) {
        onChange(value);
      }
    };
  
    return (
      <ButtonGroup isAttached variant="outline" size={size}>
        {dateOptions.map((option: any) => (
          <Button
            key={option.value}
            size={size}
            variant={selected === option.value ? 'solid' : 'outline'}
            onClick={() => handleClick(option.value)}
          >
            {option.label}
          </Button>
        ))}
      </ButtonGroup>
    );
  };

  export default DateFilterToggle;