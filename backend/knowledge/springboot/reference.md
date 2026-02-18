# Spring Boot Framework Reference

## Project Structure
- `src/main/java/com/example/` — Java sources
  - `Application.java` — `@SpringBootApplication` entry point
  - `controller/` — REST controllers
  - `service/` — Business logic
  - `repository/` — Data access (JPA)
  - `model/` or `entity/` — JPA entities
  - `dto/` — Data Transfer Objects
  - `config/` — Configuration classes
- `src/main/resources/application.properties` — Config
- `pom.xml` (Maven) or `build.gradle` (Gradle)

## Version Compatibility
- Spring Boot 3.3+: Java 17+, virtual threads support
- Spring Boot 3.x: Java 17+, Jakarta EE 9+ (javax → jakarta)
- Spring Boot 2.x: Java 8+, javax namespace

## CRITICAL: javax → jakarta Migration (Spring Boot 3)
- `javax.persistence.*` → `jakarta.persistence.*`
- `javax.servlet.*` → `jakarta.servlet.*`
- `javax.validation.*` → `jakarta.validation.*`

## JPA Entities
- `@Entity`, `@Table(name = "...")`
- `@Id`, `@GeneratedValue(strategy = GenerationType.IDENTITY)`
- `@Column`, `@ManyToOne`, `@OneToMany`
- `@CreatedDate`, `@LastModifiedDate` with `@EntityListeners`

## REST Controllers
- `@RestController` + `@RequestMapping("/api")`
- `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`
- `@PathVariable`, `@RequestBody`, `@RequestParam`
- Return `ResponseEntity<T>` for status control

## Data Access
- `JpaRepository<Entity, Long>` for CRUD
- Custom queries: `@Query("SELECT ...")`
- Method name queries: `findByUsernameAndEmail()`

## Security
- Spring Security + `spring-boot-starter-security`
- JWT: Custom `JwtFilter`, `SecurityFilterChain` bean
- `@PreAuthorize("hasRole('ADMIN')")` for method security

## Startup
- `mvn spring-boot:run` or `./gradlew bootRun`
- `application.properties` for config
- Profiles: `spring.profiles.active=dev`
