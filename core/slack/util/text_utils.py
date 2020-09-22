def get_all_users_from_blocks(blocks, users = []):
    for block in blocks:
        if block.get('type', 'unknown') == 'user':
            users.append(block)
        
        if block.get('elements', None) != None:
            users = get_all_users_from_blocks(block['elements'], users)
    
    return users