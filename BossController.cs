using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BossController : MonoBehaviour {
	const int LEFT = -1;
	const int RIGHT = 1;

	public float speed = 20;
	public float jumpspeed = 1000;
	public bool stationary = false;
	public bool followPlayer = true;
	public float walkRange = 0;
	public float visionRange = 0;
	public Vector2 shootRange;
	public float pause = 1.0f;
	public int maxHealth = 5;
	public int power = 1;
	public float shootCooldown = 1;
	private Transform shoot_loc;
	private float shoot_offx;
	private float lastX;

	public BulletController bullet;
	public float bulletSpeed = 4;
	private GameObject player;
	public GameObject deathFX;
	private Rigidbody2D body;
	public Animator anim;
	SpriteRenderer sprite;

	public Shader shaderSpriteDefault = Shader.Find("Sprites/Default");
	public Shader shaderHitFlash = Shader.Find("Sprites/HitFlash");
	private int facing = LEFT;
	private float leftPosition;
	private float rightPosition;
	private bool waiting = false;
	private float shootTimer = 0;
	private int health;

	// Use this for initialization
	void Start () {
		health = maxHealth;
		rightPosition = transform.position.x;
		leftPosition = rightPosition - walkRange;
		lastX = transform.position.x;
		player = GameObject.Find("Player");
		body = GetComponent<Rigidbody2D>();
		anim = GetComponent<Animator>();
		shoot_loc = transform.FindChild("Shoot_Loc");
		shoot_offx = shoot_loc.localPosition.x;
	}
	// Update is called once per frame
	void Update() {

		shootTimer -= Time.deltaTime;
		if (shootTimer <= 0 && InShootRange(player)) {
			Shoot();
			shootTimer = shootCooldown;
		}
		if (followPlayer && DetectPlayer(player)) {
			waiting = false;
			body.AddForce(Vector2.right * facing * speed);
		} else if (!stationary) {
			if (!waiting) {
				if (body.position.x >= rightPosition && facing == RIGHT ||
					body.position.x <= leftPosition && facing == LEFT || lastX == transform.position.x) {
					rightPosition = transform.position.x + walkRange / 2;
					leftPosition = rightPosition - walkRange;
					StartCoroutine(WaitAndChangeDirection(pause));
				} else {
					body.AddForce(Vector2.right * facing * speed);
					//body.velocity = Vector2.right * facing * speed;
				}
			}
		}

		sprite = GetComponent<SpriteRenderer>();
		sprite.flipX = facing == LEFT;
		anim.SetBool("Moving", Mathf.Abs(body.velocity.x) > 0);
		shoot_loc.localPosition = new Vector3(facing * shoot_offx, 0, 0);
		lastX = transform.position.x;
	}


	IEnumerator WaitAndChangeDirection(float seconds)
	{
		waiting = true;
		yield return new WaitForSeconds(seconds);
		if (waiting)
		{
			facing = -facing;
			waiting = false;
		}
	}

	public void Hit(int damage)
	{
		//print(name + " hit: " + damage + " damage");
		health -= damage;
		if (health <= 0)
			Die();
		StartCoroutine(HitFlash());
	}

	private IEnumerator HitFlash() {
		GetComponent<Renderer>().material.shader = shaderHitFlash;
		yield return 0; // wait one frame
		GetComponent<Renderer>().material.shader = shaderSpriteDefault;
	}

	private void Die()
	{
		//print(name + " died");
		if (deathFX) {
			GameObject deathFXOBJ = Instantiate(deathFX, transform.position, Quaternion.identity);
			Destroy(deathFXOBJ, deathFXOBJ.GetComponent<ParticleSystem>().startLifetime);
		}
		Destroy(gameObject);
	}

	void OnCollisionEnter2D(Collision2D other)
	{
		if (other.gameObject.tag == "Player")
		{
			other.gameObject.GetComponent<PlayerController>().Hit(power);
		}
	}

	private bool CheckGrounded()
	{
		return GetComponent<Rigidbody2D>().Cast(Vector2.down, new RaycastHit2D[1], 0.02f) > 0;
	}

	private bool DetectPlayer(GameObject player)
	{
		Vector3 disp = player.transform.position - transform.position;
		return disp.x * facing >= 0 && disp.sqrMagnitude <= visionRange * visionRange;
	}

	private bool InShootRange(GameObject player) {
		Vector3 disp = player.transform.position - transform.position;
		disp.x *= facing;
		return disp.x >= 0 && disp.x <= shootRange.x && Mathf.Abs(disp.y) <= shootRange.y;
	}

	private void Shoot()
	{
		anim.SetTrigger("Shoot");
		Vector3 target = player.transform.position - shoot_loc.position + new Vector3(0,0.3f,0);
		target = target / target.magnitude;

		BulletController bullet2 = Instantiate(bullet, shoot_loc.position, Quaternion.identity);
		bullet2.Initialize(target * bulletSpeed, true);

		shoot_loc.localPosition = new Vector3(facing * shoot_offx, 0.1f, 0);
		BulletController bullet3 = Instantiate(bullet, shoot_loc.position, Quaternion.identity);
		bullet3.Initialize(target * bulletSpeed, true);

		shoot_loc.localPosition = new Vector3(facing * shoot_offx, -0.1f, 0);
		BulletController bullet4 = Instantiate(bullet, shoot_loc.position, Quaternion.identity);
		bullet4.Initialize(target * bulletSpeed, true);

		shoot_loc.localPosition = new Vector3(facing * shoot_offx, 0, 0);
	}

}
