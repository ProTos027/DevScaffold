# Spring Boot Framework Reference

## Project Structure (REQUIRED — Do not deviate)
```
src/
└── main/
    ├── java/com/example/{appname}/
    │   ├── Application.java          ← @SpringBootApplication entry point
    │   ├── config/
    │   │   ├── SecurityConfig.java   ← SecurityFilterChain bean
    │   │   ├── WebSocketConfig.java  ← WebSocket/STOMP config (if ws needed)
    │   │   └── JwtUtil.java          ← JWT generation + validation utility
    │   ├── controller/               ← @RestController, delegates to service
    │   ├── service/                  ← Business logic, no HTTP awareness
    │   ├── repository/               ← JpaRepository<Entity, Long>
    │   ├── model/                    ← @Entity classes
    │   ├── dto/                      ← Request/Response DTOs (no @Entity)
    │   ├── filter/
    │   │   └── JwtAuthFilter.java    ← OncePerRequestFilter JWT filter
    │   └── websocket/                ← WebSocket handlers (if needed)
    └── resources/
        └── application.properties   ← All config values
pom.xml
```

## Version Rules (CRITICAL)
- Spring Boot 3.x: Java 17+, use `jakarta.*` NOT `javax.*`
- `javax.persistence.*` → `jakarta.persistence.*`
- `javax.servlet.*` → `jakarta.servlet.*`
- `javax.validation.*` → `jakarta.validation.*`

---

## application.properties — CRITICAL TRAPS

### NO inline comments on value lines
```properties
# WRONG — causes NumberFormatException on startup:
jwt.expiration=3600 # 1 hour

# CORRECT — comment on its own line:
# JWT expiration in seconds (1 hour)
jwt.expiration=3600
```

### JWT Secret MUST be Base64-encoded (Spring Security 6+)
```properties
# WRONG — plain string causes WeakKeyException on startup:
jwt.secret=mysecretkey

# CORRECT — Base64-encoded, minimum 256 bits (32+ bytes decoded):
jwt.secret=bXlzZWNyZXRrZXltdXN0YmVhdGxlYXN0MzJieXRlc2xvbmcK
```
Generate a valid secret: `openssl rand -base64 32`

---

## JWT Implementation (COMPLETE PATTERN)

```java
// config/JwtUtil.java (jjwt 0.12.x style)
@Component
public class JwtUtil {
    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private long expiration;

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(secret);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    public String generateToken(User user) {
        return Jwts.builder()
            .subject(user.getUsername())
            .claim("id", user.getId())
            .claim("email", user.getEmail())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expiration * 1000))
            .signWith(getSigningKey())
            .compact();
    }

    public Claims extractAllClaims(String token) {
        return Jwts.parser()
            .verifyWith(getSigningKey())
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    public Long extractUserId(String token) {
        return extractAllClaims(token).get("id", Long.class);
    }

    public String extractUsername(String token) {
        return extractAllClaims(token).getSubject();
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        try {
            String username = extractUsername(token);
            return username.equals(userDetails.getUsername()) &&
                   !extractAllClaims(token).getExpiration().before(new Date());
        } catch (JwtException e) {
            return false;
        }
    }
}
```

## JwtAuthFilter Implementation (MANDATORY CHAIN)

```java
// filter/JwtAuthFilter.java
@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {
    private final JwtUtil jwtUtil;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                    HttpServletResponse response, 
                                    FilterChain filterChain) throws ServletException, IOException {
        final String authHeader = request.getHeader("Authorization");
        final String jwt;
        final String username;

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        jwt = authHeader.substring(7);
        try {
            username = jwtUtil.extractUsername(jwt);
            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);
                if (jwtUtil.isTokenValid(jwt, userDetails)) {
                    UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                        userDetails, null, userDetails.getAuthorities()
                    );
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            }
        } catch (Exception e) {
            // Log but don't block — SecurityConfig will handle unauthorized access
        }
        filterChain.doFilter(request, response);
    }
}
```

## Spring Security Configuration

```java
// config/SecurityConfig.java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity  // Required for @PreAuthorize
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http, JwtAuthFilter jwtFilter) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/ws/**").permitAll()  // WebSocket handshake
                .anyRequest().authenticated()
            )
            // MANDATORY: Add the filter before the standard auth filter
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:3000", "http://localhost:5173"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        CorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        ((UrlBasedCorsConfigurationSource) source).registerCorsConfiguration("/**", config);
        return source;
    }
}
```

## @PreAuthorize — CORRECT SpEL Syntax (CRITICAL)

```java
// WRONG — principal.id does NOT exist on Spring's Principal interface:
@PreAuthorize("#userId == principal.id")  // ← SpEL error: 500

// CORRECT — use authentication object:
@PreAuthorize("#userId == authentication.principal.id")

// CORRECT — inject and compare manually in service:
@PutMapping("/users/{id}")
public ResponseEntity<?> updateUser(@PathVariable Long id, @RequestBody UserDto dto,
                                    Authentication authentication) {
    UserDetails userDetails = (UserDetails) authentication.getPrincipal();
    // compare id manually — do NOT use SpEL for this
    if (!userService.isOwner(id, userDetails.getUsername())) {
        return ResponseEntity.status(403).build();
    }
    return ResponseEntity.ok(userService.update(id, dto));
}
```

---

## WebSocket — Choose ONE transport (CRITICAL: declare in cross_layer_contracts)

### Option A — Raw WebSocket (simple, direct)
```java
// config/WebSocketConfig.java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(gameWebSocketHandler(), "/ws/game")
            .setAllowedOrigins("http://localhost:3000", "http://localhost:5173");
            // NO .withSockJS() here
    }
}
// cross_layer_contracts.websocket_library = "native"
// Frontend: new WebSocket("ws://localhost:8080/ws/game")
```

### Option B — SockJS + STOMP (Spring tutorial default — requires JS client lib)
```java
// config/WebSocketConfig.java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
            .setAllowedOrigins("http://localhost:3000", "http://localhost:5173")
            .withSockJS();  // ← ONLY if choosing this option
    }
    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.enableSimpleBroker("/topic", "/queue");
        registry.setApplicationDestinationPrefixes("/app");
    }
}
// cross_layer_contracts.websocket_library = "sockjs"
// Frontend MUST install: sockjs-client, @stomp/stompjs
// Frontend: const client = new Client({ brokerURL, webSocketFactory: () => new SockJS('/ws') })
```

DECLARE in cross_layer_contracts: `websocket_library = "native"` OR `"sockjs"` so frontend uses correct client.

---

## WebSocket Handler — Correct Patterns (Raw WebSocket)

```java
@Component
public class GameWebSocketHandler extends TextWebSocketHandler {

    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        // Validate JWT from query param
        String token = getTokenFromSession(session);
        if (token == null || !jwtUtil.isTokenValid(token, loadUser(token))) {
            session.close(CloseStatus.NOT_ACCEPTABLE);
            return;
        }
        sessions.put(session.getId(), session);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        // Parse, validate, process, THEN save to DB (do NOT skip persistence)
        MoveRequest move = objectMapper.readValue(message.getPayload(), MoveRequest.class);
        GameState updatedState = gameService.processMove(move);
        gameRepository.save(updatedState);  // ← ALWAYS persist state

        // Broadcast only to game participants, NOT all sessions
        String gameId = move.getGameId();
        broadcastToGame(gameId, buildGameUpdateMessage(updatedState));
    }

    private void broadcastToGame(String gameId, String message) {
        // NEVER use sessions.values() — broadcast only to game participants
        gameSessionRegistry.getSessionsForGame(gameId).forEach(session -> {
            try {
                session.sendMessage(new TextMessage(message));
            } catch (IOException e) {
                log.error("Failed to send to session {}", session.getId(), e);
            }
        });
    }

    private String getTokenFromSession(WebSocketSession session) {
        URI uri = session.getUri();
        if (uri == null) return null;
        String query = uri.getQuery();
        // Parse token=<jwt> from query string
        return Arrays.stream(query.split("&"))
            .filter(p -> p.startsWith("token="))
            .map(p -> p.substring(6))
            .findFirst().orElse(null);
    }
}
```

### WebSocket message — ALWAYS include full state
```java
// WRONG — missing fields causes frontend board not to render:
{ "type": "GAME_UPDATE" }

// CORRECT — always include boardState and currentTurn:
{
  "type": "GAME_UPDATE",
  "boardState": "rnbqkbnr/pppppppp/...",  // full FEN or board array
  "currentTurn": "white",
  "gameStatus": "ACTIVE"
}
```

---

## Escaping in Java Strings (CRITICAL — Unescaped quotes = compilation failure)

```java
// WRONG — will not compile:
String json = "{ "type": "UPDATE" }";

// CORRECT — escape inner quotes:
String json = "{ \"type\": \"UPDATE\" }";

// BEST — use text blocks (Java 15+, Spring Boot 3):
String json = """
    { "type": "UPDATE", "boardState": "%s" }
    """.formatted(boardState);
```

---

## Common Dependencies (pom.xml)
```xml
<dependencies>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-websocket</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
    <!-- JWT (jjwt 0.12.x for Spring Boot 3 compatibility) -->
    <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-api</artifactId><version>0.12.3</version></dependency>
    <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-impl</artifactId><version>0.12.3</version><scope>runtime</scope></dependency>
    <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-jackson</artifactId><version>0.12.3</version><scope>runtime</scope></dependency>
    <!-- DB -->
    <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
    <dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>runtime</scope></dependency><!-- for dev -->
</dependencies>
```
