import random
from collections import Counter
from wavecast import Wavecast, const_types

NUM_TYPES = len(const_types)  # 18
DAYS_IN_YEAR = 365
EXPECTED_PER_TYPE = DAYS_IN_YEAR / NUM_TYPES  # ~20.28


class TestWavecastGeneration:
    """Tests for the initial wavecast generation."""

    def test_generate_creates_queue_of_seven(self):
        wc = Wavecast()
        wc.generate()
        assert len(wc.queue) == 7

    def test_generate_bag_has_remaining_types(self):
        wc = Wavecast()
        wc.generate()
        assert len(wc.bag) == NUM_TYPES - 7  # 11

    def test_generate_no_duplicates_across_queue_and_bag(self):
        wc = Wavecast()
        wc.generate()
        all_types = wc.queue + wc.bag
        assert len(all_types) == NUM_TYPES
        assert set(all_types) == set(const_types)

    def test_generate_all_types_are_valid(self):
        wc = Wavecast()
        wc.generate()
        for t in wc.queue + wc.bag:
            assert t in const_types


class TestWavecastCycle:
    """Tests for the cycle (daily spin) logic."""

    def test_cycle_returns_valid_type(self):
        wc = Wavecast()
        wc.generate()
        result = wc.cycle()
        assert result in const_types

    def test_cycle_maintains_queue_size(self):
        wc = Wavecast()
        wc.generate()
        wc.cycle()
        assert len(wc.queue) == 7

    def test_cycle_pops_front_of_queue(self):
        wc = Wavecast()
        wc.generate()
        expected_next = wc.queue[0]
        result = wc.cycle()
        assert result == expected_next

    def test_bag_refills_when_empty(self):
        wc = Wavecast()
        wc.generate()
        initial_bag_size = len(wc.bag)  # 11
        # exhaust the bag
        for _ in range(initial_bag_size):
            wc.cycle()
        assert len(wc.bag) == 0
        # next cycle should refill
        wc.cycle()
        # bag was refilled to 18 then one was drawn, so 17 remain
        assert len(wc.bag) == NUM_TYPES - 1


class TestWavecastDistribution:
    """Tests that validate the statistical distribution over a simulated year.

    The bag system guarantees that within every complete 18-draw cycle, each
    type appears exactly once. Over 365 days, each type should appear between
    19 and 21 times. Any deviation beyond that range indicates a bug in the
    bag algorithm.
    """

    def _simulate_year(self, seed):
        """Simulate 365 daily spins and return a Counter of type frequencies."""
        random.seed(seed)
        wc = Wavecast()
        wc.generate()
        counts = Counter()
        for _ in range(DAYS_IN_YEAR):
            result = wc.cycle()
            counts[result] += 1
        return counts

    def test_all_types_appear(self):
        """Every type must appear at least once over 365 days."""
        counts = self._simulate_year(seed=42)
        for t in const_types:
            assert counts[t] > 0, f"{t} never appeared in 365 days"

    def test_no_type_starved(self):
        """No type should appear fewer than 19 times (floor(365/18) = 20, minus 1 for boundary)."""
        counts = self._simulate_year(seed=42)
        min_count = min(counts.values())
        min_type = min(counts, key=counts.get)
        assert min_count >= 19, (
            f"{min_type} only appeared {min_count} times in 365 days "
            f"(expected ~{EXPECTED_PER_TYPE:.1f})"
        )

    def test_no_type_dominates(self):
        """No type should appear more than 21 times (ceil(365/18) = 21)."""
        counts = self._simulate_year(seed=42)
        max_count = max(counts.values())
        max_type = max(counts, key=counts.get)
        assert max_count <= 21, (
            f"{max_type} appeared {max_count} times in 365 days "
            f"(expected ~{EXPECTED_PER_TYPE:.1f})"
        )

    def test_max_deviation_from_expected(self):
        """The spread between min and max type counts should be at most 2."""
        counts = self._simulate_year(seed=42)
        spread = max(counts.values()) - min(counts.values())
        assert spread <= 2, (
            f"Spread of {spread} is too wide. Counts: "
            + ", ".join(f"{t}: {counts[t]}" for t in const_types)
        )

    def test_distribution_across_many_seeds(self):
        """Run 100 simulations with different seeds. Every single one must stay
        within the [19, 21] range per type — this is a deterministic guarantee
        of the bag algorithm, not a statistical fluke."""
        for seed in range(100):
            counts = self._simulate_year(seed=seed)
            for t in const_types:
                assert 19 <= counts[t] <= 21, (
                    f"seed={seed}: {t} appeared {counts[t]} times "
                    f"(expected 19-21)"
                )


class TestWavecastPersistence:
    """Tests for save/load round-tripping."""

    def test_save_and_load_preserves_state(self, tmp_path):
        filepath = str(tmp_path / "wavecast.vwheel")
        random.seed(99)
        wc = Wavecast()
        wc.generate()
        wc.save(filepath)

        wc2 = Wavecast()
        wc2.load(filepath)
        assert wc2.queue == wc.queue
        assert wc2.bag == wc.bag

    def test_load_corrupt_file_regenerates(self, tmp_path):
        filepath = str(tmp_path / "wavecast.vwheel")
        with open(filepath, "w") as f:
            f.write("Bad,Data,Only,")

        wc = Wavecast()
        wc.load(filepath)
        # should have regenerated a valid wavecast
        assert len(wc.queue) == 7
        assert all(t in const_types for t in wc.queue + wc.bag)
