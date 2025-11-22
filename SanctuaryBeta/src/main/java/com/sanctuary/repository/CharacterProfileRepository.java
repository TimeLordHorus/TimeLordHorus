package com.sanctuary.repository;

import com.sanctuary.model.CharacterProfile;
import com.sanctuary.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CharacterProfileRepository extends JpaRepository<CharacterProfile, Long> {
    Optional<CharacterProfile> findByUser(User user);
    Optional<CharacterProfile> findByUserId(Long userId);
    boolean existsByUser(User user);
}
