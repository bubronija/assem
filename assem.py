import argparse
import struct
import yaml
import sys

COMMANDS = {
    'LOAD_CONST': 14,  
    'READ': 61,        
    'WRITE': 55,       
    'SUB': 32          
}

def serialize_load_const(value):
    opcode = COMMANDS['LOAD_CONST']
    packed_value = (value << 7) | opcode
    return packed_value.to_bytes(5, byteorder='little')

def read_mem(offset):
    opcode = COMMANDS['READ']
    if not (0 <= offset < 32):
        raise ValueError(f"{offset} значение должно быть от 0 до 31")
    
    packed_value = (offset << 7) | opcode
    return packed_value.to_bytes(2, byteorder='little')

def write_mem(addr):
    opcode = COMMANDS['WRITE']
    if not (0 <= addr < 2**22):
        raise ValueError(f"{addr} значение должно быть (0-{2**22-1})")
    
    packed_value = (addr << 7) | opcode
    return packed_value.to_bytes(4, byteorder='little')

def serialize_sub():
    opcode = COMMANDS['SUB']
    return opcode.to_bytes(1, byteorder='little')

def process_instruction(instr):
    cmd = instr.get('opcode')
    
    if cmd == 'LOAD_CONST':
        val = instr.get('value')
        binary = serialize_load_const(val)
        log = f"LOAD_CONST: A={COMMANDS['LOAD_CONST']}, B={val}"
        
    elif cmd == 'READ':
        offset = instr.get('offset')
        binary = read_mem(offset)
        log = f"READ:       A={COMMANDS['READ']}, B={offset}"
        
    elif cmd == 'WRITE':
        addr = instr.get('addr')
        binary = write_mem(addr)
        log = f"WRITE:      A={COMMANDS['WRITE']}, B={addr}"
        
    elif cmd == 'SUB':
        binary = serialize_sub()
        log = f"SUB:        A={COMMANDS['SUB']}"
        
    else:
        raise ValueError(f"???: {cmd}")
        
    return binary, log

def main():
    parser = argparse.ArgumentParser(description='ассемблер')
    parser.add_argument('input_file', help='путь к  файлу .yaml')
    parser.add_argument('output_file', help='путь к выходному бинарному файлу .bin')
    parser.add_argument('--test', action='store_true', help='запустить режим')
    
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            program = yaml.safe_load(f)
            
        if not program:
            print("файл программы пустой")
            return

        binary_output = bytearray()
        
        if args.test:
            print("тест")
            print(f"{'команды и значения':<30} | {'байты'}")
            print("-" * 60)

        for instr in program:
            bin_data, log_str = process_instruction(instr)
            binary_output.extend(bin_data)
            
            if args.test:
                hex_str = ", ".join([f"0x{b:02X}" for b in bin_data])
                print(f"{log_str:<30} | {hex_str}")

        with open(args.output_file, 'wb') as f:
            f.write(binary_output)
            
            if args.test:
                print("))))")
    

    except FileNotFoundError:
        print(f"ERROR файл '{args.input_file}' не найден")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR yaml: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()