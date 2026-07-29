package com.example.usermanage.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.usermanage.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}
