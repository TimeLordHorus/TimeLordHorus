package com.sanctuary.repository;

import com.sanctuary.model.Creation;
import com.sanctuary.model.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CreationRepository extends JpaRepository<Creation, Long> {
    Optional<Creation> findByGenerationId(String generationId);
    Page<Creation> findByUser(User user, Pageable pageable);
    Page<Creation> findByIsPublicTrue(Pageable pageable);
    long countByUser(User user);
}
